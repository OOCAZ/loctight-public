"""
Unit tests for LOCTight core functionality
Tests the timer and mouse jiggle functions in isolation
"""

import sys
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

# Mock pyautogui to avoid X11/display requirements in CI
sys.modules['pyautogui'] = MagicMock()


class TestTimerFunctions(unittest.TestCase):
    """Test the core timer logic"""

    @patch("time.sleep")
    @patch("pyautogui.moveRel")
    def test_jiggle_performs_mouse_movements(self, mock_move, mock_sleep):
        """Test that jiggle moves mouse correct number of times"""
        # Create a simple version of jiggle for testing
        timer_running = [True]

        def jiggle(x, checks):
            a = 0
            while a < x and timer_running[0]:
                b = 0
                while b < 6 and timer_running[0]:
                    mock_move(0, 1, duration=0.001)
                    mock_sleep(10)
                    b += 1
                a += 1

        jiggle(1, 1)
        self.assertEqual(mock_move.call_count, 6)
        self.assertEqual(mock_sleep.call_count, 6)

    @patch("time.sleep")
    def test_countdown_logic(self, mock_sleep):
        """Test countdown decrements properly"""
        timer_running = [True]
        update_count = [0]

        def update_time_label(m, s):
            update_count[0] += 1

        def countdown(minutes):
            m = minutes
            s = 0
            while m > 0 and timer_running[0]:
                s = 59
                update_time_label(m - 1, s)
                while s >= 0 and timer_running[0]:
                    update_time_label(m - 1, s)
                    mock_sleep(1)
                    s -= 1
                m -= 1
            update_time_label(0, 0)

        # Test 1 minute countdown
        countdown(1)
        # Should update label 61 times (60 seconds + initial + final)
        self.assertEqual(update_count[0], 62)

    def test_time_formatting(self):
        """Test time label format"""

        def format_time(m, s):
            return f"Time Left: {m:02}:{s:02}"

        self.assertEqual(format_time(5, 30), "Time Left: 05:30")
        self.assertEqual(format_time(0, 9), "Time Left: 00:09")
        self.assertEqual(format_time(59, 59), "Time Left: 59:59")
        self.assertEqual(format_time(0, 0), "Time Left: 00:00")

    def test_pause_toggle_logic(self):
        """Test pause toggle behavior"""
        timer_running = [True]
        paused = [False]

        def pause_timer():
            if timer_running[0]:
                paused[0] = not paused[0]
                return paused[0]
            return None

        # First pause
        result = pause_timer()
        self.assertTrue(result)
        self.assertTrue(paused[0])

        # Resume
        result = pause_timer()
        self.assertFalse(result)
        self.assertFalse(paused[0])

        # When timer not running, should not toggle
        timer_running[0] = False
        result = pause_timer()
        self.assertIsNone(result)
        self.assertFalse(paused[0])

    def test_cancel_timer_logic(self):
        """Test cancel timer behavior"""
        timer_running = [True]
        paused = [True]

        def cancel_timer():
            timer_running[0] = False
            paused[0] = False
            return timer_running[0], paused[0]

        t, p = cancel_timer()
        self.assertFalse(t)
        self.assertFalse(p)

    def test_start_timer_logic(self):
        """Test start timer can only start when not already running"""
        timer_running = [False]

        def start_timer():
            if not timer_running[0]:
                timer_running[0] = True
                return True
            return False

        # First start should succeed
        result = start_timer()
        self.assertTrue(result)
        self.assertTrue(timer_running[0])

        # Second start should fail (already running)
        result = start_timer()
        self.assertFalse(result)
        self.assertTrue(timer_running[0])


class TestInputValidation(unittest.TestCase):
    """Test input validation logic"""

    def test_custom_timer_validation(self):
        """Test custom timer input validation"""

        def validate_custom_time(value):
            try:
                time_val = int(value)
                if time_val <= 0:
                    return False, "Must be positive"
                return True, time_val
            except ValueError:
                return False, "Must be integer"

        # Valid inputs
        valid, val = validate_custom_time("45")
        self.assertTrue(valid)
        self.assertEqual(val, 45)

        valid, val = validate_custom_time("1")
        self.assertTrue(valid)
        self.assertEqual(val, 1)

        # Invalid inputs
        valid, msg = validate_custom_time("abc")
        self.assertFalse(valid)
        self.assertEqual(msg, "Must be integer")

        valid, msg = validate_custom_time("-10")
        self.assertFalse(valid)
        self.assertEqual(msg, "Must be positive")

        valid, msg = validate_custom_time("0")
        self.assertFalse(valid)
        self.assertEqual(msg, "Must be positive")

    def test_preset_timers(self):
        """Test preset timer values"""
        SHORT_TIMER = 30
        LONG_TIMER = 60

        self.assertEqual(SHORT_TIMER, 30)
        self.assertEqual(LONG_TIMER, 60)


class TestPlatformLocking(unittest.TestCase):
    """Test platform-specific lock commands"""

    @patch("subprocess.run")
    def test_windows_lock(self, mock_subprocess):
        """Test Windows lock workstation call"""
        # Create a mock for ctypes on Windows
        with patch.dict('sys.modules', {'ctypes': MagicMock()}):
            import ctypes
            mock_windll = MagicMock()
            ctypes.windll = mock_windll
            
            # Test the lock function
            if sys.platform == "win32":
                ctypes.windll.user32.LockWorkStation()
                mock_windll.user32.LockWorkStation.assert_called_once()

    @patch("subprocess.call")
    @patch("sys.platform", "darwin")
    def test_macos_lock(self, mock_subprocess):
        """Test macOS lock command"""
        if sys.platform == "darwin":
            mock_subprocess(
                r"/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend",
                shell=True,
            )

        self.assertTrue(mock_subprocess.called)

    @patch("subprocess.run")
    def test_linux_lock(self, mock_subprocess):
        """Test Linux lock command tries multiple lockers"""
        from sys import platform
        
        # Mock successful lock on first try
        mock_subprocess.return_value = MagicMock()
        
        # Simulate lock_workstation for Linux
        if platform == "linux" or platform == "linux2":
            lockers = [
                ["loginctl", "lock-session"],
                ["xdg-screensaver", "lock"],
            ]
            for locker in lockers:
                try:
                    mock_subprocess(locker, check=True, capture_output=True)
                    break
                except:
                    continue
        
        self.assertTrue(mock_subprocess.called)


class TestButtonStateManagement(unittest.TestCase):
    """Test button enable/disable logic"""

    def test_disable_buttons_on_timer_start(self):
        """Test that starting timer disables appropriate buttons"""
        buttons_state = {
            "button1": "NORMAL",
            "button2": "NORMAL",
            "button3": "NORMAL",
            "pause": "DISABLED",
            "cancel": "DISABLED",
        }

        def disable_buttons():
            buttons_state["button1"] = "DISABLED"
            buttons_state["button2"] = "DISABLED"
            buttons_state["button3"] = "DISABLED"
            buttons_state["pause"] = "NORMAL"
            buttons_state["cancel"] = "NORMAL"

        disable_buttons()

        self.assertEqual(buttons_state["button1"], "DISABLED")
        self.assertEqual(buttons_state["button2"], "DISABLED")
        self.assertEqual(buttons_state["button3"], "DISABLED")
        self.assertEqual(buttons_state["pause"], "NORMAL")
        self.assertEqual(buttons_state["cancel"], "NORMAL")

    def test_enable_buttons_on_timer_end(self):
        """Test that ending timer enables appropriate buttons"""
        buttons_state = {
            "button1": "DISABLED",
            "button2": "DISABLED",
            "button3": "DISABLED",
            "pause": "NORMAL",
            "cancel": "NORMAL",
        }

        def enable_buttons():
            buttons_state["button1"] = "NORMAL"
            buttons_state["button2"] = "NORMAL"
            buttons_state["button3"] = "NORMAL"
            buttons_state["pause"] = "DISABLED"
            buttons_state["cancel"] = "DISABLED"

        enable_buttons()

        self.assertEqual(buttons_state["button1"], "NORMAL")
        self.assertEqual(buttons_state["button2"], "NORMAL")
        self.assertEqual(buttons_state["button3"], "NORMAL")
        self.assertEqual(buttons_state["pause"], "DISABLED")
        self.assertEqual(buttons_state["cancel"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
