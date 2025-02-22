import threading


class ThreadingManager:
    """
    Manages multi-threading for real-time data processing and trading execution.
    """

    def __init__(self):
        """
        Initialize threading manager with an empty dictionary to track threads.
        """
        self.threads = {}

    def start_thread(self, name, target, *args):
        """
        Start a new thread for a given function.

        :param name: Name of the thread.
        :param target: Function to be executed in the thread.
        :param args: Arguments for the target function.
        """
        if name in self.threads and self.threads[name].is_alive():
            print(f"Thread {name} is already running.")
            return

        thread = threading.Thread(target=target, args=args, daemon=True)
        self.threads[name] = thread
        thread.start()
        print(f"Thread {name} started.")

    def stop_thread(self, name):
        """
        Stop a running thread (best effort, since Python does not support forceful thread termination).

        :param name: Name of the thread to stop.
        """
        if name in self.threads:
            print(f"Stopping thread {name}...")
            self.threads[name] = None
        else:
            print(f"Thread {name} not found.")

    def list_threads(self):
        """
        List all active threads.
        """
        return [name for name, thread in self.threads.items() if thread and thread.is_alive()]
