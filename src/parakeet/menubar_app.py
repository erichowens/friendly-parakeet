"""Mac menu bar app for Friendly Parakeet."""

import rumps
import threading
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import random
import os

from .parakeet import Parakeet
from .brilliant_budgies import BrilliantBudgies
from .ide_watcher import IDEWatcher
from .subscription_manager import SubscriptionManager
from .sounds import SoundPlayer


class ParakeetMenuBarApp(rumps.App):
    """Menu bar app for Friendly Parakeet."""

    def __init__(self):
        """Initialize the menu bar app."""
        super(ParakeetMenuBarApp, self).__init__(
            "🦜",
            quit_button=None,
            icon="assets/parakeet_icon.png",
            template=True  # Makes icon work in light/dark mode
        )

        # Initialize Parakeet core
        self.parakeet = Parakeet()
        self.brilliant_budgies = BrilliantBudgies(self.parakeet)
        self.ide_watcher = IDEWatcher(self.parakeet)
        self.subscription = SubscriptionManager(self.parakeet.config.data_dir)
        self.sound_player = SoundPlayer(enabled=True)

        # State tracking
        self.notification_count = 0
        self.last_scan = datetime.now()
        self.sound_enabled = True
        self.brilliant_budgie_enabled = True
        self.ide_monitoring_enabled = False

        # Create menu items
        self.menu = [
            rumps.MenuItem("📊 Dashboard", callback=self.open_dashboard),
            rumps.MenuItem("🔍 Scan Projects", callback=self.scan_projects),
            None,  # Separator
            rumps.MenuItem("👁️ IDE Monitoring"),
            rumps.MenuItem("📍 Recent Breadcrumbs"),
            rumps.MenuItem("💡 Brilliant Budgies"),
            None,  # Separator
            rumps.MenuItem("💳 Subscription"),
            None,  # Separator
            rumps.MenuItem("🔊 Sounds", callback=self.toggle_sounds),
            rumps.MenuItem("⚙️ Preferences", callback=self.open_preferences),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        # Initialize submenus
        self.setup_ide_monitoring_menu()
        self.setup_subscription_menu()

        # Start background threads
        self.start_background_tasks()

        # Play startup sound
        self.play_sound("hello")

    def update_icon_badge(self, count: int):
        """Update the number indicator on the parakeet icon.

        Args:
            count: Number to display (0 hides the badge)
        """
        if count > 0:
            # Update title to show count
            self.title = f"🦜 {count}"

            # Play alert sound for important changes
            if count > self.notification_count:
                self.play_sound("alert")

        else:
            self.title = "🦜"

        self.notification_count = count

    def play_sound(self, sound_type: str):
        """Play budgie sounds for different events.

        Args:
            sound_type: Type of sound to play (hello, alert, eureka, chirp, happy)
        """
        if not self.sound_enabled:
            return

        # Map legacy sound types to new ones
        sound_map = {
            "startup": "hello",
            "idea": "eureka",
            "success": "happy"
        }

        # Use mapped sound type or original
        mapped_type = sound_map.get(sound_type, sound_type)

        # Play sound using the sound player
        if not self.sound_player.play(mapped_type):
            # Fallback to system sound if sound file not found
            rumps.notification(
                title="🦜 Friendly Parakeet",
                subtitle=f"{sound_type.capitalize()} Sound",
                message="",
                sound=True
            )

    @rumps.clicked("📊 Dashboard")
    def open_dashboard(self, _):
        """Open the web dashboard."""
        subprocess.Popen(["parakeet", "dashboard"])
        self.play_sound("chirp")

        rumps.notification(
            title="🦜 Dashboard Opening",
            subtitle="Your coding companion is ready!",
            message="Opening dashboard at http://localhost:5000"
        )

    @rumps.clicked("🔍 Scan Projects")
    def scan_projects(self, _):
        """Manually trigger project scan."""
        self.play_sound("chirp")

        # Run scan in background
        thread = threading.Thread(target=self._run_scan)
        thread.daemon = True
        thread.start()

    def _run_scan(self):
        """Run project scan and update UI."""
        projects = self.parakeet.scan_and_update()

        # Count important changes
        inactive_count = 0
        breadcrumb_count = 0

        for project in projects:
            inactivity = self.parakeet.tracker.get_inactivity_days(project['path'])
            if inactivity >= 7:
                inactive_count += 1

            breadcrumbs = self.parakeet.breadcrumbs.get_breadcrumbs(project['path'])
            breadcrumb_count += len(breadcrumbs)

        # Update badge with important items
        self.update_icon_badge(breadcrumb_count)

        # Update breadcrumb menu
        self.update_breadcrumb_menu()

        # Notify if there are important findings
        if inactive_count > 0:
            self.play_sound("alert")
            rumps.notification(
                title="🦜 Projects Need Attention",
                subtitle=f"{inactive_count} projects have been inactive",
                message="Click to view breadcrumbs and resume work!"
            )
        else:
            self.play_sound("happy")
            rumps.notification(
                title="🦜 All Projects Active",
                subtitle="Great job staying on top of your work!",
                message=f"Scanned {len(projects)} projects"
            )

        self.last_scan = datetime.now()

    def update_breadcrumb_menu(self):
        """Update the breadcrumb submenu with recent items."""
        breadcrumb_menu = self.menu["📍 Recent Breadcrumbs"]
        breadcrumb_menu.clear()

        all_breadcrumbs = self.parakeet.breadcrumbs.get_all_breadcrumbs()

        if not all_breadcrumbs:
            breadcrumb_menu.add(rumps.MenuItem("No breadcrumbs yet"))
            return

        # Get most recent breadcrumbs
        recent_breadcrumbs = []
        for path, crumbs in all_breadcrumbs.items():
            if crumbs:
                latest = crumbs[-1]
                latest['project_path'] = path
                recent_breadcrumbs.append(latest)

        # Sort by timestamp
        recent_breadcrumbs.sort(key=lambda x: x['timestamp'], reverse=True)

        # Add to menu (limit to 10)
        for crumb in recent_breadcrumbs[:10]:
            project_name = Path(crumb['project_path']).name
            inactive_days = crumb['inactivity_days']

            menu_item = rumps.MenuItem(
                f"🔴 {project_name} ({inactive_days} days)",
                callback=lambda sender, crumb=crumb: self.show_breadcrumb_detail(crumb)
            )
            breadcrumb_menu.add(menu_item)

    def show_breadcrumb_detail(self, breadcrumb):
        """Show detailed breadcrumb information.

        Args:
            breadcrumb: Breadcrumb data to display
        """
        self.play_sound("chirp")

        # Get first prompt suggestion
        prompt = breadcrumb['prompt_suggestions'][0] if breadcrumb['prompt_suggestions'] else ""

        rumps.notification(
            title=f"📍 {breadcrumb['project_name']}",
            subtitle=f"Inactive for {breadcrumb['inactivity_days']} days",
            message=prompt
        )

        # Copy prompt to clipboard
        subprocess.run(["pbcopy"], input=prompt.encode())

    def update_brilliant_budgie_menu(self):
        """Update the Brilliant Budgies submenu with recent ideas."""
        budgie_menu = self.menu["💡 Brilliant Budgies"]
        budgie_menu.clear()

        # Add toggle option
        toggle_item = rumps.MenuItem(
            "✅ Enabled" if self.brilliant_budgie_enabled else "❌ Disabled",
            callback=self.toggle_brilliant_budgies
        )
        budgie_menu.add(toggle_item)
        budgie_menu.add(None)  # Separator

        # Get recent brilliant budgie ideas
        ideas = self.brilliant_budgies.get_recent_ideas(limit=5)

        if not ideas:
            budgie_menu.add(rumps.MenuItem("No ideas yet - let me think..."))
            return

        for idea in ideas:
            menu_item = rumps.MenuItem(
                f"💡 {idea['title']}",
                callback=lambda sender, idea=idea: self.show_budgie_idea(idea)
            )
            budgie_menu.add(menu_item)

    def show_budgie_idea(self, idea):
        """Show detailed Brilliant Budgie idea.

        Args:
            idea: Idea data to display
        """
        self.play_sound("eureka")

        rumps.notification(
            title=f"💡 Brilliant Budgie Idea!",
            subtitle=idea['title'],
            message=idea['description']
        )

        # Open detailed view if requested
        if rumps.alert(
            title=f"💡 {idea['title']}",
            message=f"{idea['description']}\n\nWould you like to implement this idea?",
            ok="Yes, let's do it!",
            cancel="Maybe later"
        ):
            # Create implementation task
            self.brilliant_budgies.create_implementation_task(idea)
            self.play_sound("happy")

    @rumps.clicked("🔊 Sounds")
    def toggle_sounds(self, sender):
        """Toggle sound effects on/off."""
        self.sound_enabled = not self.sound_enabled
        sender.title = "🔊 Sounds" if self.sound_enabled else "🔇 Sounds"

        if self.sound_enabled:
            self.play_sound("chirp")

        rumps.notification(
            title="🦜 Sound Settings",
            subtitle=f"Sounds {'enabled' if self.sound_enabled else 'disabled'}",
            message=""
        )

    def toggle_brilliant_budgies(self, sender):
        """Toggle Brilliant Budgies feature on/off."""
        self.brilliant_budgie_enabled = not self.brilliant_budgie_enabled
        sender.title = "✅ Enabled" if self.brilliant_budgie_enabled else "❌ Disabled"

        if self.brilliant_budgie_enabled:
            self.play_sound("eureka")
            rumps.notification(
                title="💡 Brilliant Budgies Enabled",
                subtitle="Your parakeet will think of helpful ideas!",
                message="Ideas will be generated during off-hours"
            )
        else:
            rumps.notification(
                title="💡 Brilliant Budgies Disabled",
                subtitle="Your parakeet is taking a break",
                message=""
            )

    @rumps.clicked("⚙️ Preferences")
    def open_preferences(self, _):
        """Open preferences window."""
        # For now, open config file in editor
        config_path = Path.home() / ".parakeet" / "config.yaml"
        subprocess.run(["open", "-t", str(config_path)])

        rumps.notification(
            title="⚙️ Preferences",
            subtitle="Opening configuration file",
            message="Edit and save to update settings"
        )

    def setup_ide_monitoring_menu(self):
        """Setup the IDE monitoring submenu."""
        ide_menu = self.menu["👁️ IDE Monitoring"]
        ide_menu.clear()

        # Toggle monitoring
        toggle_item = rumps.MenuItem(
            "✅ Monitoring Active" if self.ide_monitoring_enabled else "❌ Start Monitoring",
            callback=self.toggle_ide_monitoring
        )
        ide_menu.add(toggle_item)
        ide_menu.add(None)  # Separator

        # Show active IDEs
        ide_menu.add(rumps.MenuItem("Active IDEs:", callback=None))
        active_ides = self.ide_watcher.detect_active_ides()
        if active_ides:
            for ide in active_ides:
                ide_item = rumps.MenuItem(
                    f"  • {ide['type'].title()}: {ide['name']}",
                    callback=None
                )
                ide_menu.add(ide_item)
        else:
            ide_menu.add(rumps.MenuItem("  No IDEs detected", callback=None))

        ide_menu.add(None)  # Separator

        # Coding stats
        stats_item = rumps.MenuItem("📈 Coding Stats", callback=self.show_coding_stats)
        ide_menu.add(stats_item)

        # Recent insights
        insights_item = rumps.MenuItem("💭 Recent Insights", callback=self.show_ide_insights)
        ide_menu.add(insights_item)

    def toggle_ide_monitoring(self, sender):
        """Toggle IDE monitoring on/off."""
        self.ide_monitoring_enabled = not self.ide_monitoring_enabled

        if self.ide_monitoring_enabled:
            self.ide_watcher.start_monitoring()
            sender.title = "✅ Monitoring Active"
            self.play_sound("chirp")

            rumps.notification(
                title="👁️ IDE Monitoring Started",
                subtitle="Watching your coding activity",
                message="I'll track your progress and detect when you need help!"
            )

            # Update the icon to show monitoring is active
            self.update_monitoring_status()
        else:
            self.ide_watcher.stop_monitoring()
            sender.title = "❌ Start Monitoring"

            rumps.notification(
                title="👁️ IDE Monitoring Stopped",
                subtitle="No longer watching IDE activity",
                message=""
            )

        # Refresh the menu
        self.setup_ide_monitoring_menu()

    def show_coding_stats(self, _):
        """Show coding statistics."""
        stats = self.ide_watcher.get_coding_stats(days=7)

        # Format stats for display
        active_hours = stats['total_active_time'] / 3600
        productivity = stats.get('productivity_score', 0)

        message = f"""
📊 Your Coding Stats (Last 7 Days):

⏱️ Active Coding Time: {active_hours:.1f} hours
📁 Files Edited: {stats['total_files_edited']}
🎯 Flow States: {stats['flow_states']}
🚧 Stuck Moments: {stats['stuck_moments']}
🏆 Productivity Score: {productivity}%

Keep up the great work! 🦜
"""

        rumps.alert(
            title="📈 Coding Statistics",
            message=message.strip(),
            ok="Cool!"
        )

        self.play_sound("chirp")

    def show_ide_insights(self, _):
        """Show recent IDE insights."""
        insights = self.ide_watcher.get_recent_insights(limit=5)

        if not insights:
            rumps.notification(
                title="💭 No Insights Yet",
                subtitle="Keep coding and I'll learn your patterns!",
                message=""
            )
            return

        # Show the most recent insight
        latest = insights[0]
        insight_type = latest.get('type', 'general')
        message = latest.get('message', 'Keep coding!')

        # Special handling for different insight types
        if insight_type == 'stuck_detected':
            self.play_sound("alert")
            suggestions = latest.get('suggestions', [])
            if suggestions:
                message += "\n\nTry:\n" + "\n".join(f"• {s}" for s in suggestions[:3])

            rumps.notification(
                title="🤔 Looks Like You're Stuck",
                subtitle=f"On {Path(latest.get('file', 'unknown')).name}",
                message=message
            )
        elif insight_type == 'flow_state':
            self.play_sound("happy")
            rumps.notification(
                title="🌊 You're In The Flow!",
                subtitle=f"Coding for {latest.get('duration_minutes', 0):.0f} minutes",
                message="Keep it up! Your parakeet is impressed!"
            )
        elif insight_type == 'long_session':
            self.play_sound("alert")
            rumps.notification(
                title="⏰ Long Coding Session",
                subtitle=f"{latest.get('duration_hours', 0):.1f} hours and counting",
                message=latest.get('suggestion', 'Consider taking a break!')
            )
        else:
            rumps.notification(
                title="💭 IDE Insight",
                subtitle=insight_type.replace('_', ' ').title(),
                message=message
            )

    def update_monitoring_status(self):
        """Update the menu bar icon to show monitoring status."""
        if self.ide_monitoring_enabled:
            # Add a dot or indicator to show monitoring is active
            if "👁" not in self.title:
                current_title = self.title
                # Add eye emoji to indicate monitoring
                if self.notification_count > 0:
                    self.title = f"🦜👁 {self.notification_count}"
                else:
                    self.title = "🦜👁"
        else:
            # Remove monitoring indicator
            if "👁" in self.title:
                if self.notification_count > 0:
                    self.title = f"🦜 {self.notification_count}"
                else:
                    self.title = "🦜"

    def setup_subscription_menu(self):
        """Setup the subscription submenu."""
        sub_menu = self.menu["💳 Subscription"]
        sub_menu.clear()

        # Get subscription info
        sub_info = self.subscription.get_subscription_info()

        if sub_info["authenticated"]:
            # Show user info
            sub_menu.add(rumps.MenuItem(f"👤 {sub_info['user']}", callback=None))
            sub_menu.add(rumps.MenuItem(f"📦 {sub_info['tier'].title()} Plan", callback=None))

            # Usage info
            usage = sub_info.get("usage", {})
            used = usage.get("monthly_usage", 0)
            limit = usage.get("monthly_limit", 10)
            sub_menu.add(rumps.MenuItem(f"📊 Usage: {used}/{limit}", callback=None))

            sub_menu.add(None)  # Separator

            # Upgrade/Downgrade options
            if sub_info["tier"] == "free":
                sub_menu.add(rumps.MenuItem("⬆️ Upgrade to Friendly ($4.99/mo)",
                                           callback=lambda _: self.upgrade_subscription("friendly")))
                sub_menu.add(rumps.MenuItem("⬆️ Upgrade to Professional ($9.99/mo)",
                                           callback=lambda _: self.upgrade_subscription("professional")))
            elif sub_info["tier"] == "friendly":
                sub_menu.add(rumps.MenuItem("⬆️ Upgrade to Professional ($9.99/mo)",
                                           callback=lambda _: self.upgrade_subscription("professional")))
                sub_menu.add(rumps.MenuItem("⬆️ Upgrade to Team ($19.99/mo)",
                                           callback=lambda _: self.upgrade_subscription("team")))
            elif sub_info["tier"] == "professional":
                sub_menu.add(rumps.MenuItem("⬆️ Upgrade to Team ($19.99/mo)",
                                           callback=lambda _: self.upgrade_subscription("team")))

            if sub_info["tier"] != "free":
                sub_menu.add(rumps.MenuItem("❌ Cancel Subscription", callback=self.cancel_subscription))

            sub_menu.add(None)  # Separator
            sub_menu.add(rumps.MenuItem("🚪 Logout", callback=self.logout))
        else:
            # Not authenticated
            sub_menu.add(rumps.MenuItem("🔐 Login", callback=self.show_login))
            sub_menu.add(rumps.MenuItem("✨ Sign Up", callback=self.show_signup))
            sub_menu.add(None)  # Separator
            sub_menu.add(rumps.MenuItem("ℹ️ About Subscriptions", callback=self.show_subscription_info))

    def show_login(self, _):
        """Show login dialog."""
        window = rumps.Window(
            title="Login to Friendly Parakeet",
            message="Enter your username:",
            default_text="",
            ok="Next",
            cancel="Cancel"
        )
        response = window.run()

        if response.clicked:
            username = response.text

            window = rumps.Window(
                title="Login to Friendly Parakeet",
                message="Enter your password:",
                default_text="",
                ok="Login",
                cancel="Cancel"
            )
            # Note: This is not secure for password entry in production
            # You'd want a proper password dialog
            response = window.run()

            if response.clicked:
                password = response.text

                # Login asynchronously
                import asyncio
                result = asyncio.run(self.subscription.login(username, password))

                if result["success"]:
                    self.play_sound("happy")
                    rumps.notification(
                        title="✅ Login Successful",
                        subtitle=f"Welcome back, {username}!",
                        message="You can now use AI features"
                    )
                    self.setup_subscription_menu()
                else:
                    self.play_sound("alert")
                    rumps.alert(
                        title="Login Failed",
                        message=result.get("error", "Invalid credentials")
                    )

    def show_signup(self, _):
        """Show signup dialog."""
        # Email
        window = rumps.Window(
            title="Sign Up for Friendly Parakeet",
            message="Enter your email:",
            default_text="",
            ok="Next",
            cancel="Cancel"
        )
        response = window.run()
        if not response.clicked:
            return
        email = response.text

        # Username
        window = rumps.Window(
            title="Sign Up for Friendly Parakeet",
            message="Choose a username:",
            default_text="",
            ok="Next",
            cancel="Cancel"
        )
        response = window.run()
        if not response.clicked:
            return
        username = response.text

        # Password
        window = rumps.Window(
            title="Sign Up for Friendly Parakeet",
            message="Create a password (8+ characters):",
            default_text="",
            ok="Sign Up",
            cancel="Cancel"
        )
        response = window.run()
        if not response.clicked:
            return
        password = response.text

        # Signup asynchronously
        import asyncio
        result = asyncio.run(self.subscription.signup(email, username, password))

        if result["success"]:
            self.play_sound("happy")
            rumps.notification(
                title="✅ Account Created!",
                subtitle=f"Welcome to Friendly Parakeet, {username}!",
                message="You have 10 free AI requests to start"
            )
            self.setup_subscription_menu()
        else:
            self.play_sound("alert")
            rumps.alert(
                title="Signup Failed",
                message=result.get("error", "Could not create account")
            )

    def upgrade_subscription(self, tier: str):
        """Upgrade subscription to a new tier."""
        prices = {
            "friendly": "$4.99/month",
            "professional": "$9.99/month",
            "team": "$19.99/month"
        }

        if rumps.alert(
            title=f"Upgrade to {tier.title()}",
            message=f"Upgrade your subscription to {tier.title()} for {prices[tier]}?",
            ok="Upgrade",
            cancel="Cancel"
        ):
            # Open web browser for payment
            # In production, you'd integrate Stripe payment flow
            import webbrowser
            webbrowser.open(f"https://friendlyparakeet.com/subscribe?tier={tier}")

            rumps.notification(
                title="💳 Complete Payment",
                subtitle="Opening payment page in browser",
                message="Complete your subscription upgrade online"
            )

    def cancel_subscription(self, _):
        """Cancel subscription."""
        if rumps.alert(
            title="Cancel Subscription",
            message="Are you sure you want to cancel your subscription? It will remain active until the end of the billing period.",
            ok="Yes, Cancel",
            cancel="Keep Subscription"
        ):
            import asyncio
            result = asyncio.run(self.subscription.cancel_subscription())

            if result["success"]:
                self.play_sound("chirp")
                rumps.notification(
                    title="Subscription Cancelled",
                    subtitle="We're sorry to see you go!",
                    message="Your subscription will remain active until the end of the billing period"
                )
                self.setup_subscription_menu()
            else:
                rumps.alert(
                    title="Cancellation Failed",
                    message=result.get("error", "Could not cancel subscription")
                )

    def logout(self, _):
        """Logout from account."""
        if rumps.alert(
            title="Logout",
            message="Are you sure you want to logout?",
            ok="Logout",
            cancel="Cancel"
        ):
            import asyncio
            asyncio.run(self.subscription.logout())
            self.play_sound("chirp")
            rumps.notification(
                title="👋 Logged Out",
                subtitle="See you later!",
                message="You can login again anytime"
            )
            self.setup_subscription_menu()

    def show_subscription_info(self, _):
        """Show subscription information."""
        info = """
🦜 Friendly Parakeet AI Subscriptions

Get AI-powered coding assistance without managing API keys!

📦 Plans:

• FREE: 10 AI requests/month
  Perfect for trying out AI features

• FRIENDLY ($4.99/mo): 500 requests
  Great for individual developers
  - Brilliant Budgie ideas
  - Priority support

• PROFESSIONAL ($9.99/mo): 2000 requests
  For active developers
  - Advanced AI models
  - Custom prompts
  - Priority support

• TEAM ($19.99/mo): Unlimited
  For teams and power users
  - Unlimited AI requests
  - Team collaboration
  - API access

All paid plans include:
✅ Secure server-side AI processing
✅ No API key management
✅ Usage tracking
✅ Cancel anytime
"""
        rumps.alert(
            title="Subscription Plans",
            message=info.strip(),
            ok="Got it!"
        )

    def quit_app(self, _):
        """Quit the application."""
        # Stop IDE monitoring if active
        if self.ide_monitoring_enabled:
            self.ide_watcher.stop_monitoring()

        # Close subscription manager
        import asyncio
        asyncio.run(self.subscription.close())

        self.play_sound("chirp")
        rumps.quit_application()

    def start_background_tasks(self):
        """Start background monitoring tasks."""
        # Auto-scan thread
        scan_thread = threading.Thread(target=self._auto_scan_loop)
        scan_thread.daemon = True
        scan_thread.start()

        # Brilliant Budgies thread
        budgie_thread = threading.Thread(target=self._brilliant_budgie_loop)
        budgie_thread.daemon = True
        budgie_thread.start()

    def _auto_scan_loop(self):
        """Background loop for automatic scanning."""
        while True:
            try:
                # Wait for scan interval (default 5 minutes)
                time.sleep(300)

                # Check if it's been long enough since last scan
                if datetime.now() - self.last_scan > timedelta(minutes=5):
                    self._run_scan()

            except Exception as e:
                print(f"Error in auto-scan: {e}")

    def _brilliant_budgie_loop(self):
        """Background loop for Brilliant Budgies idea generation."""
        while True:
            try:
                # Check every hour
                time.sleep(3600)

                if not self.brilliant_budgie_enabled:
                    continue

                # Generate ideas during off-hours (late night or early morning)
                current_hour = datetime.now().hour
                if current_hour < 6 or current_hour > 22:
                    # Off-hours - time to think!
                    new_ideas = self.brilliant_budgies.generate_ideas()

                    if new_ideas:
                        self.play_sound("eureka")
                        self.update_brilliant_budgie_menu()

                        rumps.notification(
                            title="💡 New Brilliant Budgie Ideas!",
                            subtitle=f"{len(new_ideas)} new ideas generated",
                            message="Your parakeet has been thinking..."
                        )

                        # Update badge to show new ideas
                        current_count = self.notification_count
                        self.update_icon_badge(current_count + len(new_ideas))

            except Exception as e:
                print(f"Error in Brilliant Budgies: {e}")


def main():
    """Run the menu bar app."""
    app = ParakeetMenuBarApp()
    app.run()


if __name__ == "__main__":
    main()