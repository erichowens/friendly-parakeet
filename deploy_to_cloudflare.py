#!/usr/bin/env python3
"""
🦜 Friendly Parakeet - Interactive Cloudflare Pages Deployer
Automates deployment of your websites to Cloudflare Pages
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown

console = Console()

class CloudflareDeployer:
    def __init__(self):
        self.website_dir = Path(__file__).parent / "website"
        self.sites = {
            "friendlyparakeet.com": self.website_dir / "friendlyparakeet.com",
            "brilliantbudgies.com": self.website_dir / "brilliantbudgies.com"
        }

    def run_command(self, cmd, cwd=None, capture=True):
        """Run a shell command and return output"""
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(cmd, shell=True, cwd=cwd, check=True)
                return ""
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error:[/red] {e.stderr if e.stderr else str(e)}")
            return None

    def check_prerequisites(self):
        """Check if required tools are installed"""
        console.print("\n[bold cyan]🔍 Checking prerequisites...[/bold cyan]\n")

        checks = {
            "Git": ("git --version", "https://git-scm.com/downloads"),
            "Node.js": ("node --version", "https://nodejs.org"),
            "npm": ("npm --version", "Comes with Node.js"),
            "Wrangler CLI": ("wrangler --version", "npm install -g wrangler"),
        }

        results = []
        all_good = True

        for tool, (cmd, install_info) in checks.items():
            version = self.run_command(cmd)
            if version:
                results.append((tool, "✅", version.split('\n')[0]))
            else:
                results.append((tool, "❌", f"Not installed - {install_info}"))
                all_good = False

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Version/Info", style="dim")

        for row in results:
            table.add_row(*row)

        console.print(table)

        if not all_good:
            console.print("\n[yellow]⚠️  Please install missing tools before continuing.[/yellow]")
            return False

        console.print("\n[green]✅ All prerequisites met![/green]")
        return True

    def select_site(self):
        """Let user select which site to deploy"""
        console.print("\n[bold cyan]📦 Which site do you want to deploy?[/bold cyan]\n")

        options = list(self.sites.keys())
        for i, site in enumerate(options, 1):
            console.print(f"  {i}. [cyan]{site}[/cyan]")
        console.print(f"  {len(options) + 1}. [cyan]Both sites[/cyan]")

        choice = Prompt.ask(
            "\nSelect option",
            choices=[str(i) for i in range(1, len(options) + 2)],
            default="1"
        )

        if int(choice) == len(options) + 1:
            return options
        else:
            return [options[int(choice) - 1]]

    def check_git_status(self, site_path):
        """Check if site is a git repo and has uncommitted changes"""
        console.print(f"\n[bold cyan]🔍 Checking git status...[/bold cyan]")

        if not (site_path / ".git").exists():
            console.print("[yellow]Not a git repository. Initializing...[/yellow]")
            self.run_command("git init", cwd=site_path, capture=False)
            console.print("[green]✅ Git repository initialized[/green]")

        status = self.run_command("git status --porcelain", cwd=site_path)
        if status:
            console.print(f"\n[yellow]📝 You have uncommitted changes:[/yellow]")
            console.print(status)

            if Confirm.ask("\n💾 Commit these changes?", default=True):
                message = Prompt.ask(
                    "Commit message",
                    default="Deploy: Update website"
                )
                self.run_command(f'git add .', cwd=site_path, capture=False)
                self.run_command(f'git commit -m "{message}"', cwd=site_path, capture=False)
                console.print("[green]✅ Changes committed[/green]")

    def setup_github_repo(self, site_name, site_path):
        """Set up GitHub repository"""
        console.print(f"\n[bold cyan]🐙 Setting up GitHub repository...[/bold cyan]")

        remote = self.run_command("git remote get-url origin", cwd=site_path)

        if remote:
            console.print(f"[green]✅ Remote already configured:[/green] {remote}")
            return remote

        console.print("\n[yellow]No GitHub remote found.[/yellow]")
        console.print("\n[bold]Please create a GitHub repository:[/bold]")
        console.print(f"1. Go to https://github.com/new")
        console.print(f"2. Name it: {site_name}")
        console.print(f"3. Keep it public or private")
        console.print(f"4. Don't initialize with README (we already have code)")

        input("\n[cyan]Press Enter when you've created the repo...[/cyan]")

        repo_url = Prompt.ask(
            "\n🔗 Enter your GitHub repo URL",
            default=f"https://github.com/YOUR_USERNAME/{site_name}.git"
        )

        self.run_command(f'git remote add origin {repo_url}', cwd=site_path, capture=False)
        self.run_command('git branch -M main', cwd=site_path, capture=False)

        console.print("\n[bold cyan]📤 Pushing to GitHub...[/bold cyan]")
        self.run_command('git push -u origin main', cwd=site_path, capture=False)

        console.print("[green]✅ Code pushed to GitHub![/green]")
        return repo_url

    def build_site(self, site_path):
        """Build the Next.js site"""
        console.print(f"\n[bold cyan]🏗️  Building site...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing dependencies...", total=None)

            # Check if node_modules exists
            if not (site_path / "node_modules").exists():
                self.run_command("npm install", cwd=site_path, capture=False)

            progress.update(task, description="Building production bundle...")
            result = self.run_command("npm run build", cwd=site_path, capture=False)

            if result is not None:
                console.print("[green]✅ Build successful![/green]")
                return True
            else:
                console.print("[red]❌ Build failed. Please check the errors above.[/red]")
                return False

    def deploy_with_wrangler(self, site_name, site_path):
        """Deploy using Wrangler CLI"""
        console.print(f"\n[bold cyan]🚀 Deploying to Cloudflare Pages...[/bold cyan]")

        # Check if logged in
        auth_check = self.run_command("wrangler whoami")
        if not auth_check or "not authenticated" in auth_check.lower():
            console.print("\n[yellow]🔐 You need to log in to Cloudflare[/yellow]")
            console.print("Opening browser for authentication...")
            self.run_command("wrangler login", capture=False)

        project_name = site_name.replace('.com', '').replace('.', '-')

        console.print(f"\n[bold]Deploying as project:[/bold] [cyan]{project_name}[/cyan]")

        # Deploy
        deploy_cmd = f'wrangler pages deploy .next --project-name={project_name} --branch=main'

        with console.status("[bold green]Uploading to Cloudflare..."):
            result = self.run_command(deploy_cmd, cwd=site_path, capture=False)

        if result is not None:
            console.print(f"\n[green]✅ Deployed successfully![/green]")
            console.print(f"\n[bold]Your site is live at:[/bold]")
            console.print(f"[cyan]https://{project_name}.pages.dev[/cyan]")
            return True
        return False

    def configure_custom_domain(self, site_name, project_name):
        """Guide user through custom domain setup"""
        console.print(f"\n[bold cyan]🌐 Custom Domain Setup[/bold cyan]")

        console.print(f"""
[bold]To connect {site_name}:[/bold]

1. Go to Cloudflare Dashboard: https://dash.cloudflare.com
2. Navigate to: Workers & Pages → {project_name} → Custom domains
3. Click "Set up a custom domain"
4. Enter: {site_name}
5. Cloudflare will auto-configure DNS (you own the domain!)
6. Also add: www.{site_name}

[green]Since you own the domain on Cloudflare, DNS will configure automatically![/green]
        """)

        if Confirm.ask("\n✅ Have you configured the custom domain?", default=False):
            console.print(f"\n[green]🎉 Great! Your site will be live at https://{site_name} in 1-5 minutes![/green]")

    def show_next_steps(self, site_name):
        """Show next steps after deployment"""
        md = f"""
# 🎉 Deployment Complete!

## Your Site
- **Production**: https://{site_name}
- **Preview**: https://{site_name.replace('.com', '')}.pages.dev

## Next Steps

1. **Enable Analytics**
   - Go to Cloudflare Dashboard → Web Analytics
   - Enable for {site_name}

2. **Set up Email**
   - Cloudflare Email Routing (free!)
   - Create hello@{site_name}
   - Forward to your personal email

3. **SEO Setup**
   - Submit to Google Search Console
   - Create sitemap.xml
   - Add to Bing Webmaster Tools

4. **Monitor Performance**
   - Check Core Web Vitals
   - Set up uptime monitoring
   - Review security settings

## Future Deployments

Every time you push to GitHub `main` branch, Cloudflare will automatically rebuild and deploy!

```bash
git add .
git commit -m "Update website"
git push
```

That's it! ✨
        """

        console.print(Panel(Markdown(md), title="🦜 Success!", border_style="green"))

    def deploy_site(self, site_name):
        """Complete deployment workflow for a site"""
        console.clear()
        console.print(Panel.fit(
            f"[bold cyan]Deploying {site_name}[/bold cyan]",
            border_style="cyan"
        ))

        site_path = self.sites[site_name]

        if not site_path.exists():
            console.print(f"[red]❌ Site directory not found:[/red] {site_path}")
            return False

        # Step 1: Check git status
        self.check_git_status(site_path)

        # Step 2: GitHub setup
        repo_url = self.setup_github_repo(site_name, site_path)

        # Step 3: Build
        if not self.build_site(site_path):
            return False

        # Step 4: Deploy
        project_name = site_name.replace('.com', '').replace('.', '-')
        if not self.deploy_with_wrangler(site_name, site_path):
            return False

        # Step 5: Custom domain
        self.configure_custom_domain(site_name, project_name)

        # Step 6: Next steps
        self.show_next_steps(site_name)

        return True

    def run(self):
        """Main deployment flow"""
        console.print(Panel.fit(
            "[bold green]🦜 Friendly Parakeet[/bold green]\n[cyan]Interactive Cloudflare Pages Deployer[/cyan]",
            border_style="green"
        ))

        # Check prerequisites
        if not self.check_prerequisites():
            return

        # Select site(s)
        sites_to_deploy = self.select_site()

        # Deploy each site
        for site_name in sites_to_deploy:
            success = self.deploy_site(site_name)

            if not success:
                console.print(f"\n[red]❌ Deployment failed for {site_name}[/red]")
                if not Confirm.ask("Continue with other sites?", default=True):
                    break

            if len(sites_to_deploy) > 1:
                console.print("\n" + "="*80 + "\n")

        console.print("\n[bold green]✨ All done![/bold green]")

def main():
    try:
        deployer = CloudflareDeployer()
        deployer.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Deployment cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red] {str(e)}")
        console.print("\n[dim]Run with DEBUG=1 for full traceback[/dim]")
        if os.getenv('DEBUG'):
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
