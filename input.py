import pygame
from pynput import keyboard
import queue

class InputManager:
    """
    Unified input manager handling keyboard and mouse input from both pygame and pynput.
    Supports registering actions dynamically and getting directional input vectors.
    Thread-safe with pynput.
    """

    def __init__(self):
        # ----------------------
        # Keyboard
        # ----------------------
        self.keys_held = set()             # All currently pressed keys
        self.keys_just_pressed = set()     # Pressed this frame
        self.keys_just_released = set()    # Released this frame

        # Thread-safe queue for pynput events
        self.key_event_queue = queue.Queue()

        # ----------------------
        # Mouse
        # ----------------------
        self.mouse_buttons = {'left': False, 'right': False, 'middle': False}
        self.mouse_buttons_pressed = {'left': False, 'right': False, 'middle': False}
        self.mouse_buttons_released = {'left': False, 'right': False, 'middle': False}
        self.mouse_pos = (0, 0)
        self.mouse_scroll = [0, 0]  # [x, y]
        self.mouse_pos_changed = False
        self.mouse_scroll_changed = False

        # ----------------------
        # Action mapping
        # ----------------------
        self.action_map = {}

        # ----------------------
        # Start pynput listener
        # ----------------------
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    # ----------------------
    # Pynput callbacks
    # ----------------------
    def _on_press(self, key):
        try:
            k = str(key.char).lower()
        except AttributeError:
            k = str(key)
        self.key_event_queue.put(('press', k))

    def _on_release(self, key):
        try:
            k = str(key.char).lower()
        except AttributeError:
            k = str(key)
        self.key_event_queue.put(('release', k))

    # ----------------------
    # Query functions
    # ----------------------
    def key_held(self, k): return k in self.keys_held
    def key_pressed(self, k): return k in self.keys_just_pressed
    def key_released(self, k): return k in self.keys_just_released

    def register_action(self, action_name, keys):
        if not isinstance(keys, list):
            keys = [keys]
        self.action_map[action_name] = keys

    def action_active(self, action_name):
        keys = self.action_map.get(action_name, [])
        return any(k in self.keys_held for k in keys)

    def action_pressed(self, action_name):
        keys = self.action_map.get(action_name, [])
        return any(k in self.keys_just_pressed for k in keys)

    def action_released(self, action_name):
        keys = self.action_map.get(action_name, [])
        return any(k in self.keys_just_released for k in keys)

    # ----------------------
    # Directional Input
    # ----------------------
    def get_input_vector(self, horizontal=('a', 'd'), vertical=('w', 's')):
        x = int(horizontal[1] in self.keys_held) - int(horizontal[0] in self.keys_held)
        y = int(vertical[1] in self.keys_held) - int(vertical[0] in self.keys_held)
        return [x, y]

    # ----------------------
    # Mouse Input
    # ----------------------
    def get_mouse_pos(self):
        return self.mouse_pos

    def get_mouse_buttons(self):
        return self.mouse_buttons

    def get_mouse_scroll(self):
        scroll = self.mouse_scroll.copy()
        self.mouse_scroll = [0, 0]  # Reset after reading
        self.mouse_scroll_changed = False
        return scroll

    # ----------------------
    # Event handling (main thread)
    # ----------------------
    def handle_pygame_events(self):
        """
        Call every frame:
        - Handles pygame events
        - Processes pynput events in a thread-safe way
        - Updates all mouse and keyboard states
        Returns False if QUIT event is detected.
        """

        if not pygame.get_init():
            return True

        running = True

        # --- 1) Process pygame events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos_changed = True
                self.mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_buttons['left'] = True
                    self.mouse_buttons_pressed['left'] = True
                elif event.button == 2:
                    self.mouse_buttons['middle'] = True
                    self.mouse_buttons_pressed['middle'] = True
                elif event.button == 3:
                    self.mouse_buttons['right'] = True
                    self.mouse_buttons_pressed['right'] = True
                elif event.button == 4:
                    self.mouse_scroll_changed = True
                    self.mouse_scroll[1] = 1
                elif event.button == 5:
                    self.mouse_scroll_changed = True
                    self.mouse_scroll[1] = -1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_buttons['left'] = False
                    self.mouse_buttons_released['left'] = True
                elif event.button == 2:
                    self.mouse_buttons['middle'] = False
                    self.mouse_buttons_released['middle'] = True
                elif event.button == 3:
                    self.mouse_buttons['right'] = False
                    self.mouse_buttons_released['right'] = True

        # --- 2) Process pynput events from queue ---
        while not self.key_event_queue.empty():
            action, key = self.key_event_queue.get()
            if action == 'press':
                if key not in self.keys_held:
                    self.keys_just_pressed.add(key)
                self.keys_held.add(key)
            elif action == 'release':
                if key in self.keys_held:
                    self.keys_held.discard(key)
                    self.keys_just_released.add(key)

        # --- 3) Return running ---
        return running

    # ----------------------
    # Clear transient states (call at the very end of the frame)
    # ----------------------
    def clear_transient_states(self):
        """Call at the end of each frame, after reading inputs"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        for b in self.mouse_buttons_pressed:
            self.mouse_buttons_pressed[b] = False
        for b in self.mouse_buttons_released:
            self.mouse_buttons_released[b] = False
        self.mouse_pos_changed = False
        self.mouse_scroll_changed = False
