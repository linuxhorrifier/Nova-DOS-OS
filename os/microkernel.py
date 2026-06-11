import os
import json
import ast
from copy import deepcopy


class MicrokernelError(Exception):
    pass


class DiskValidationError(MicrokernelError):
    pass


class SandboxError(MicrokernelError):
    pass


class ProcessState:
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"


class ProcessExit(Exception):
    def __init__(self, code=0):
        super().__init__(f"Process exit: {code}")
        self.code = code


class ProcessYield(Exception):
    pass


class Process:
    def __init__(self, pid, name, code, user=None, cwd="/", parent_pid=None, memory_limit=4096):
        self.pid = pid
        self.name = name
        self.code = code
        self.user = user
        self.cwd = cwd
        self.parent_pid = parent_pid
        self.state = ProcessState.NEW
        self.exit_code = None
        self.memory_handles = []
        self.memory_limit = memory_limit
        self.allocated_bytes = 0
        self.children = []
        self.start_time = None
        self.end_time = None

    def allocate_bytes(self, size):
        self.allocated_bytes += size

    def free_bytes(self, size):
        self.allocated_bytes = max(0, self.allocated_bytes - size)


class MemoryManager:
    def __init__(self, total_bytes=65536, page_size=256):
        self.total_bytes = total_bytes
        self.page_size = page_size
        self.next_handle = 1
        self.allocations = {}

    def allocate(self, pid, size):
        if size <= 0:
            raise ValueError("Allocation size must be greater than zero.")
        if size > self.total_bytes:
            raise ValueError("Requested memory exceeds total simulated memory.")
        handle = self.next_handle
        self.next_handle += 1
        self.allocations[handle] = {
            "pid": pid,
            "size": size,
            "buffer": bytearray(size),
        }
        return handle

    def free(self, pid, handle):
        allocation = self.allocations.get(handle)
        if allocation is None:
            raise ValueError("Invalid memory handle.")
        if allocation["pid"] != pid:
            raise ValueError("Memory handle does not belong to this process.")
        del self.allocations[handle]

    def read(self, pid, handle, offset, size):
        allocation = self.allocations.get(handle)
        if allocation is None:
            raise ValueError("Invalid memory handle.")
        if allocation["pid"] != pid:
            raise ValueError("Memory handle does not belong to this process.")
        if offset < 0 or size < 0 or offset + size > allocation["size"]:
            raise ValueError("Memory read out of bounds.")
        return bytes(allocation["buffer"][offset:offset + size])

    def write(self, pid, handle, offset, data):
        allocation = self.allocations.get(handle)
        if allocation is None:
            raise ValueError("Invalid memory handle.")
        if allocation["pid"] != pid:
            raise ValueError("Memory handle does not belong to this process.")
        if offset < 0 or offset > allocation["size"]:
            raise ValueError("Memory write out of bounds.")
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError("Data must be bytes or string.")
        if offset + len(data) > allocation["size"]:
            raise ValueError("Memory write out of bounds.")
        allocation["buffer"][offset:offset + len(data)] = data


class Microkernel:
    SAFE_BUILTINS = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "pow": pow,
        "print": print,
        "range": range,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }

    DANGEROUS_NAMES = {
        "open",
        "eval",
        "exec",
        "compile",
        "__import__",
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "ctypes",
        "pickle",
        "marshal",
        "builtins",
        "__builtins__",
    }

    DANGEROUS_ATTRS = {
        "system",
        "popen",
        "remove",
        "unlink",
        "rmdir",
        "chmod",
        "chown",
        "exec",
        "fork",
        "spawn",
        "__globals__",
        "__code__",
        "__closure__",
        "__func__",
        "__self__",
    }

    def __init__(self, disk_file, default_disk=None):
        self.disk_file = disk_file
        self.backup_file = disk_file + ".bak"
        self.default_disk = default_disk or {}
        self.disk = None
        self.process_table = {}
        self.ready_queue = []
        self.next_pid = 1
        self.memory_manager = MemoryManager(total_bytes=65536, page_size=256)
        self.max_process_memory = 8192
        self.scheduler_log = []

    def atomic_write_json(self, path, data):
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def ensure_disk_structure(self, disk):
        if disk is None:
            disk = {}

        disk.setdefault("settings", deepcopy(self.default_disk.get("settings", {})))
        disk.setdefault("directories", deepcopy(self.default_disk.get("directories", ["/"])))
        disk.setdefault("files", deepcopy(self.default_disk.get("files", {})))
        disk.setdefault("users", deepcopy(self.default_disk.get("users", {})))
        disk.setdefault("current_user", None)
        disk.setdefault("current_dir", "/")
        disk.setdefault("prompt", self.default_disk.get("prompt", ""))
        disk.setdefault("bank", deepcopy(self.default_disk.get("bank", {})))

        if "/" not in disk["directories"]:
            disk["directories"].insert(0, "/")

        return disk

    def load_disk(self):
        try:
            if os.path.exists(self.disk_file):
                with open(self.disk_file, "r") as f:
                    data = json.load(f)
                try:
                    self.atomic_write_json(self.backup_file, data)
                except Exception:
                    pass
                self.disk = self.ensure_disk_structure(data)
                return self.disk
            if os.path.exists(self.backup_file):
                with open(self.backup_file, "r") as f:
                    self.disk = self.ensure_disk_structure(json.load(f))
                    return self.disk
        except Exception:
            pass

        self.disk = deepcopy(self.default_disk)
        self.ensure_disk_structure(self.disk)
        return self.disk

    def save_disk(self, disk=None):
        disk = disk if disk is not None else self.disk
        if disk is None:
            raise DiskValidationError("No disk state available to save.")

        self.ensure_disk_structure(disk)
        try:
            self.atomic_write_json(self.disk_file, disk)
        except Exception:
            raise
        try:
            self.atomic_write_json(self.backup_file, disk)
        except Exception:
            pass

    def create_process(self, code, name=None, user=None, cwd=None, parent_pid=None, memory_limit=None):
        pid = self.next_pid
        self.next_pid += 1
        if cwd is None:
            cwd = self.disk.get("current_dir", "/") if self.disk else "/"
        if memory_limit is None:
            memory_limit = self.max_process_memory

        process = Process(
            pid=pid,
            name=name or f"process_{pid}",
            code=code,
            user=user,
            cwd=cwd,
            parent_pid=parent_pid,
            memory_limit=memory_limit,
        )
        process.state = ProcessState.READY
        self.process_table[pid] = process
        self.ready_queue.append(pid)
        if parent_pid is not None and parent_pid in self.process_table:
            self.process_table[parent_pid].children.append(pid)
        return process

    def terminate_process(self, pid, code=0):
        process = self.process_table.get(pid)
        if process is None:
            return
        process.state = ProcessState.TERMINATED
        process.exit_code = code
        self.cleanup_process(pid)

    def cleanup_process(self, pid):
        process = self.process_table.get(pid)
        if process is None:
            return
        for handle in list(process.memory_handles):
            try:
                self.memory_manager.free(pid, handle)
            except Exception:
                pass
        process.memory_handles.clear()
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)

    def schedule(self, time_slice=1):
        if not self.ready_queue:
            return None
        pid = self.ready_queue.pop(0)
        process = self.process_table.get(pid)
        if process is None or process.state != ProcessState.READY:
            return None
        self.run_process(pid)
        return process

    def run_process(self, pid):
        process = self.process_table.get(pid)
        if process is None:
            raise MicrokernelError(f"No process with PID {pid}")
        if process.state == ProcessState.TERMINATED:
            return process

        process.state = ProcessState.RUNNING
        process.start_time = process.start_time or os.times()
        try:
            helpers = {
                "syscall": self.create_syscall_handler(process),
                "process": process,
            }
            self.execute_sandboxed(process.code, helpers=helpers)
        except ProcessYield:
            process.state = ProcessState.READY
            self.ready_queue.append(pid)
        except ProcessExit as e:
            process.state = ProcessState.TERMINATED
            process.exit_code = e.code
            self.cleanup_process(pid)
        except SandboxError:
            process.state = ProcessState.TERMINATED
            process.exit_code = -1
            self.cleanup_process(pid)
        except Exception:
            process.state = ProcessState.TERMINATED
            process.exit_code = -1
            self.cleanup_process(pid)
        else:
            if process.state == ProcessState.RUNNING:
                process.state = ProcessState.TERMINATED
                if process.exit_code is None:
                    process.exit_code = 0
                self.cleanup_process(pid)
        finally:
            process.end_time = os.times()

    def create_syscall_handler(self, process):
        def syscall(call_name, *args, **kwargs):
            return self.handle_syscall(process, call_name, *args, **kwargs)
        return syscall

    def handle_syscall(self, process, call_name, *args, **kwargs):
        method = getattr(self, f"syscall_{call_name}", None)
        if method is None:
            raise SandboxError(f"Unknown syscall: {call_name}")
        return method(process, *args, **kwargs)

    def syscall_getpid(self, process):
        return process.pid

    def syscall_getppid(self, process):
        return process.parent_pid

    def syscall_getcwd(self, process):
        return process.cwd

    def syscall_chdir(self, process, path):
        process.cwd = self.normalize_path(path, process.cwd)
        return process.cwd

    def syscall_exit(self, process, code=0):
        raise ProcessExit(code)

    def syscall_yield(self, process):
        raise ProcessYield()

    def syscall_list_processes(self, process):
        return [
            {
                "pid": p.pid,
                "name": p.name,
                "state": p.state,
                "user": p.user,
                "cwd": p.cwd,
            }
            for p in self.process_table.values()
        ]

    def syscall_spawn(self, process, file_path, *args, **kwargs):
        code = self.read_file(file_path, self.disk)
        return self.create_process(code, name=file_path, user=process.user, cwd=process.cwd, parent_pid=process.pid)

    def syscall_read_file(self, process, path):
        return self.read_file(path, self.disk)

    def syscall_write_file(self, process, path, content):
        file_path = self.write_file(path, content, self.disk)
        return file_path

    def syscall_list_dir(self, process, path=""):
        contents = self.get_directory_contents(path or process.cwd, self.disk)
        return contents or {}

    def syscall_make_dir(self, process, path):
        return self.make_directory(path, self.disk)

    def syscall_remove_dir(self, process, path):
        return self.remove_directory(path, self.disk)

    def syscall_delete_file(self, process, path):
        return self.delete_file(path, self.disk)

    def syscall_find_text(self, process, term):
        return self.find_text(term, self.disk)

    def syscall_alloc(self, process, size):
        if process.allocated_bytes + size > process.memory_limit:
            raise SandboxError("Process memory limit exceeded.")
        handle = self.memory_manager.allocate(process.pid, size)
        process.memory_handles.append(handle)
        process.allocate_bytes(size)
        return handle

    def syscall_free(self, process, handle):
        allocation = self.memory_manager.allocations.get(handle)
        if allocation is None:
            raise SandboxError("Invalid memory handle.")
        process.free_bytes(allocation["size"])
        process.memory_handles.remove(handle)
        self.memory_manager.free(process.pid, handle)

    def syscall_read_mem(self, process, handle, offset, size):
        data = self.memory_manager.read(process.pid, handle, offset, size)
        return data.decode("utf-8", errors="replace")

    def syscall_write_mem(self, process, handle, offset, data):
        self.memory_manager.write(process.pid, handle, offset, data)
        return True

    def syscall_sysinfo(self, process):
        return {
            "total_processes": len(self.process_table),
            "ready_queue": list(self.ready_queue),
            "memory_total": self.memory_manager.total_bytes,
            "memory_used": sum(allocation["size"] for allocation in self.memory_manager.allocations.values()),
        }

    def syscall_terminate(self, process, pid):
        self.terminate_process(pid)
        return True

    def syscall_rename_process(self, process, pid, new_name):
        target = self.process_table.get(pid)
        if target is None:
            raise SandboxError("Process not found.")
        target.name = new_name
        return True

    def syscall_get_memory_map(self, process):
        return {
            handle: {
                "size": allocation["size"],
                "pid": allocation["pid"],
            }
            for handle, allocation in self.memory_manager.allocations.items()
        }

    def syscall_open(self, process, path, mode="r"):
        if "w" in mode or "a" in mode:
            raise SandboxError("Direct file open in sandbox is not allowed.")
        return self.read_file(path, self.disk)

    def syscall_eval(self, process, expression):
        return self.evaluate_sandboxed(expression)

    def syscall_assert(self, process, condition, message="Assertion failed"):
        if not condition:
            raise SandboxError(message)

    def syscall_get_time(self, process):
        return os.times()

    def syscall_get_user(self, process):
        return process.user

    def syscall_set_user(self, process, user):
        process.user = user
        return True

    def syscall_get_prompt(self, process):
        return self.disk.get("prompt")

    def syscall_set_prompt(self, process, prompt):
        self.disk["prompt"] = prompt
        self.save_disk(self.disk)
        return prompt

    def normalize_path(self, path, current_dir="/"):
        path = (path or "").replace("\\", "/").strip()
        if path == "":
            return current_dir or "/"

        if path.startswith("/"):
            normalized = os.path.normpath(path)
        else:
            base = current_dir.rstrip("/") if current_dir else ""
            if base == "":
                normalized = os.path.normpath(f"/{path}")
            else:
                normalized = os.path.normpath(f"{base}/{path}")

        if not normalized.startswith("/"):
            normalized = "/" + normalized
        return normalized

    def ensure_directory(self, path, disk):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        if target == "/":
            if "/" not in disk["directories"]:
                disk["directories"].append("/")
            return target

        current = ""
        for part in target.strip("/").split("/"):
            current += "/" + part
            if current not in disk["directories"]:
                disk["directories"].append(current)
        return target

    def path_is_dir(self, path, disk):
        return self.normalize_path(path, disk.get("current_dir", "/")) in disk["directories"]

    def path_is_file(self, path, disk):
        return self.normalize_path(path, disk.get("current_dir", "/")) in disk["files"]

    def get_directory_contents(self, dir_path, disk):
        target = self.normalize_path(dir_path, disk.get("current_dir", "/"))
        if target != "/" and target not in disk["directories"]:
            return None

        prefix = target if target.endswith("/") else f"{target}/"
        contents = {}

        for directory in disk["directories"]:
            if directory == target:
                continue
            if directory.startswith(prefix):
                remainder = directory[len(prefix):].split("/", 1)[0]
                if remainder:
                    contents[remainder] = {"type": "DIR"}

        for file_path, content in disk["files"].items():
            if file_path.startswith(prefix):
                remainder = file_path[len(prefix):].split("/", 1)[0]
                if remainder and "/" not in file_path[len(prefix):]:
                    contents[remainder] = {"type": "FILE", "size": len(content)}

        return contents

    def read_file(self, path, disk):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        if target not in disk["files"]:
            raise DiskValidationError(f"File not found: {path}")
        return disk["files"][target]

    def write_file(self, path, content, disk, save=True):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        parent = os.path.dirname(target)
        self.ensure_directory(parent, disk)
        disk["files"][target] = content
        if save:
            self.save_disk(disk)
        return target

    def delete_file(self, path, disk, save=True):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        if target not in disk["files"]:
            raise DiskValidationError(f"File not found: {path}")
        del disk["files"][target]
        if save:
            self.save_disk(disk)

    def copy_file(self, src, dst, disk, save=True):
        source = self.normalize_path(src, disk.get("current_dir", "/"))
        destination = self.normalize_path(dst, disk.get("current_dir", "/"))
        if source not in disk["files"]:
            raise DiskValidationError(f"Source file not found: {src}")

        if destination in disk["directories"]:
            destination = self.normalize_path(os.path.join(destination, os.path.basename(source)).replace("\\", "/"), disk.get("current_dir", "/"))

        parent = os.path.dirname(destination)
        self.ensure_directory(parent, disk)
        disk["files"][destination] = disk["files"][source]
        if save:
            self.save_disk(disk)
        return destination

    def move_file(self, src, dst, disk, save=True):
        destination = self.copy_file(src, dst, disk, save=False)
        self.delete_file(src, disk, save=False)
        if save:
            self.save_disk(disk)
        return destination

    def make_directory(self, path, disk, save=True):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        if target in disk["directories"]:
            return target
        self.ensure_directory(target, disk)
        if save:
            self.save_disk(disk)
        return target

    def remove_directory(self, path, disk, save=True):
        target = self.normalize_path(path, disk.get("current_dir", "/"))
        if target == "/":
            raise DiskValidationError("Cannot remove root directory.")
        if target not in disk["directories"]:
            raise DiskValidationError(f"Directory not found: {path}")

        prefix = f"{target}/"
        for directory in disk["directories"]:
            if directory != target and directory.startswith(prefix):
                raise DiskValidationError("Directory is not empty.")
        for file_path in disk["files"]:
            if file_path.startswith(prefix):
                raise DiskValidationError("Directory is not empty.")

        disk["directories"].remove(target)
        if save:
            self.save_disk(disk)

    def rename_path(self, src, dst, disk, save=True):
        source = self.normalize_path(src, disk.get("current_dir", "/"))
        destination = self.normalize_path(dst, disk.get("current_dir", "/"))
        if source in disk["files"]:
            self.move_file(source, destination, disk, save=False)
            if save:
                self.save_disk(disk)
            return destination

        if source in disk["directories"]:
            if destination in disk["directories"]:
                raise DiskValidationError("Destination already exists.")
            disk["directories"].append(destination)
            for directory in list(disk["directories"]):
                if directory.startswith(source + "/"):
                    disk["directories"].append(directory.replace(source, destination, 1))
                    disk["directories"].remove(directory)
            for file_path in list(disk["files"]):
                if file_path.startswith(source + "/"):
                    disk["files"][file_path.replace(source, destination, 1)] = disk["files"].pop(file_path)
            disk["directories"].remove(source)
            if save:
                self.save_disk(disk)
            return destination

        raise DiskValidationError(f"Source not found: {src}")

    def find_text(self, term, disk):
        term_lower = (term or "").lower()
        results = []
        for path, content in disk["files"].items():
            if term_lower in path.lower() or term_lower in content.lower():
                results.append(path)
        return sorted(results)

    def authenticate_user(self, username, password, disk):
        if username in disk.get("users", {}) and disk["users"][username].get("password") == password:
            return True
        return False

    def rename_user(self, old_username, new_username, disk, save=True):
        if old_username not in disk.get("users", {}):
            raise DiskValidationError(f"User not found: {old_username}")
        if new_username in disk.get("users", {}):
            raise DiskValidationError(f"User already exists: {new_username}")
        disk["users"][new_username] = disk["users"].pop(old_username)
        if save:
            self.save_disk(disk)

    def change_password(self, username, new_password, disk, save=True):
        if username not in disk.get("users", {}):
            raise DiskValidationError(f"User not found: {username}")
        disk["users"][username]["password"] = new_password
        if save:
            self.save_disk(disk)

    def format_disk(self):
        disk = deepcopy(self.default_disk)
        self.ensure_disk_structure(disk)
        self.disk = disk
        self.save_disk(disk)
        return disk

    def safe_builtins(self):
        return dict(self.SAFE_BUILTINS)

    def get_safe_globals(self, helpers=None):
        exec_globals = {"__name__": "__main__", "__builtins__": self.safe_builtins()}
        if helpers:
            exec_globals.update(helpers)
        return exec_globals

    def is_code_safe(self, src):
        try:
            tree = ast.parse(src)
        except Exception:
            return False, "syntax error"

        class SafeVisitor(ast.NodeVisitor):
            def __init__(self, parent):
                self.issues = set()
                self.parent = parent

            def visit_Import(self, node):
                self.issues.add("import")

            def visit_ImportFrom(self, node):
                self.issues.add("import")

            def visit_Call(self, node):
                func = node.func
                if isinstance(func, ast.Name) and func.id in self.parent.DANGEROUS_NAMES:
                    self.issues.add(func.id)
                if isinstance(func, ast.Attribute) and func.attr in self.parent.DANGEROUS_ATTRS:
                    self.issues.add(func.attr)
                self.generic_visit(node)

            def visit_Attribute(self, node):
                if node.attr.startswith("__") or node.attr in self.parent.DANGEROUS_ATTRS:
                    self.issues.add(node.attr)
                self.generic_visit(node)

            def visit_Name(self, node):
                if node.id in self.parent.DANGEROUS_NAMES or node.id.startswith("__"):
                    self.issues.add(node.id)
                self.generic_visit(node)

        visitor = SafeVisitor(self)
        visitor.visit(tree)
        if visitor.issues:
            return False, ", ".join(sorted(visitor.issues))
        return True, None

    def execute_sandboxed(self, code, helpers=None):
        safe, why = self.is_code_safe(code)
        if not safe:
            raise SandboxError(f"unsafe constructs detected: {why}")

        exec_globals = self.get_safe_globals(helpers)
        exec(code, exec_globals)

    def evaluate_sandboxed(self, expression, helpers=None):
        safe, why = self.is_code_safe(expression)
        if not safe:
            raise SandboxError(f"unsafe constructs detected: {why}")
        return eval(expression, self.get_safe_globals(helpers))
