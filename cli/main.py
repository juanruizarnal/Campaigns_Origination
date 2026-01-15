"""Main CLI entry point for Alter-5 Origination Engine.

This module provides the command-line interface for running agents,
managing campaigns, and performing administrative tasks.

Usage:
    # Run a specific agent
    python -m cli.main agent run buscador --sector "Renewables"
    
    # Check system status
    python -m cli.main status
    
    # List campaigns
    python -m cli.main campaign list
"""

from typing import Optional

import typer

from config.settings import get_settings
from core.logging import configure_logging, get_logger

# Create main Typer app
app = typer.Typer(
    name="origination",
    help="Alter-5 Origination Automation Engine CLI",
    add_completion=False,
    no_args_is_help=True,
)

# Sub-applications for organized commands
agent_app = typer.Typer(help="AI Agent management commands")
campaign_app = typer.Typer(help="Campaign management commands")
company_app = typer.Typer(help="Company management commands")
fei_app = typer.Typer(help="FEI evaluation commands")
context_app = typer.Typer(help="Market context analysis commands")
message_app = typer.Typer(help="Message generation commands")
search_app = typer.Typer(help="Company search commands")

# Register sub-apps
app.add_typer(agent_app, name="agent")
app.add_typer(campaign_app, name="campaign")
app.add_typer(company_app, name="company")
app.add_typer(fei_app, name="fei")
app.add_typer(context_app, name="context")
app.add_typer(message_app, name="message")
app.add_typer(search_app, name="search")


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity."""
    level = "DEBUG" if verbose else None
    configure_logging(level=level)


# ==============================================================================
# ROOT COMMANDS
# ==============================================================================


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed status"),
    campaign_id: Optional[str] = typer.Option(None, "--campaign-id", "-c", help="Show specific campaign metrics"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table or json"),
) -> None:
    """Check system status and show KPI metrics.
    
    Shows:
    - Companies by FEI status
    - Active campaigns and metrics
    - Recent FEI evaluations
    - System connectivity status
    
    Examples:
        python -m cli.main status
        python -m cli.main status --campaign-id recXXX
        python -m cli.main status --format json
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo("📊 Alter-5 Origination Engine Status")
    typer.echo("=" * 50)
    
    # Check settings
    try:
        settings = get_settings()
        typer.echo("\n✅ Configuration loaded")
        if verbose:
            typer.echo(f"   • Airtable Base: {settings.AIRTABLE_BASE_ID}")
            typer.echo(f"   • Language: {settings.DEFAULT_LANGUAGE}")
            typer.echo(f"   • Cooling Off: {settings.COOLING_OFF_DAYS} days")
            typer.echo(f"   • Max Targets: {settings.MAX_TARGETS_PER_CAMPAIGN}")
    except Exception as e:
        typer.echo(f"❌ Config error: {e}", err=True)
        raise typer.Exit(1)
    
    # Get Airtable data
    typer.echo("\n📈 KPI Metrics")
    typer.echo("-" * 50)
    
    try:
        from core.airtable_client import AirtableClient
        client = AirtableClient()
        
        # Get companies by FEI status
        typer.echo("\n🏢 Companies by FEI Status:")
        try:
            companies = client.query_records("companies", max_records=1000)
            fei_counts: dict[str, int] = {}
            for company in companies:
                status = company.get("fields", {}).get("FEI_Status", "Unknown")
                fei_counts[status] = fei_counts.get(status, 0) + 1
            
            total_companies = len(companies)
            typer.echo(f"   Total: {total_companies}")
            for status, count in sorted(fei_counts.items()):
                pct = (count / total_companies * 100) if total_companies > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                typer.echo(f"   • {status:<20} {count:>4} ({pct:>5.1f}%) {bar}")
        except Exception as e:
            typer.echo(f"   ⚠️ Could not fetch companies: {e}")
        
        # Get active campaigns
        typer.echo("\n🎯 Recent Campaigns:")
        try:
            campaigns = client.query_records("campaigns", max_records=10)
            if campaigns:
                for camp in campaigns[:5]:
                    fields = camp.get("fields", {})
                    name = fields.get("Campaign_Name", "Unnamed")[:30]
                    status = fields.get("Status", "Unknown")
                    targets = fields.get("Target_Count", 0)
                    typer.echo(f"   • {name:<30} Status: {status:<12} Targets: {targets}")
            else:
                typer.echo("   No campaigns found")
        except Exception as e:
            typer.echo(f"   ⚠️ Could not fetch campaigns: {e}")
        
        # Get specific campaign details if requested
        if campaign_id:
            typer.echo(f"\n📊 Campaign Details: {campaign_id}")
            try:
                campaign = client.get_record("campaigns", campaign_id)
                if campaign:
                    fields = campaign.get("fields", {})
                    typer.echo(f"   Name: {fields.get('Campaign_Name', 'N/A')}")
                    typer.echo(f"   Status: {fields.get('Status', 'N/A')}")
                    typer.echo(f"   Trigger: {fields.get('Trigger', 'N/A')}")
                    typer.echo(f"   Created: {fields.get('Created_Date', 'N/A')}")
                    
                    # Get targets for this campaign
                    targets = client.query_records(
                        "campaign_targets",
                        filter_formula=f"{{Campaign_ID}} = '{campaign_id}'",
                    )
                    if targets:
                        status_counts: dict[str, int] = {}
                        for target in targets:
                            ts = target.get("fields", {}).get("Outreach_Status", "Pending")
                            status_counts[ts] = status_counts.get(ts, 0) + 1
                        
                        typer.echo(f"\n   Target Status Breakdown:")
                        for ts, count in sorted(status_counts.items()):
                            typer.echo(f"     • {ts}: {count}")
            except Exception as e:
                typer.echo(f"   ⚠️ Could not fetch campaign: {e}")
        
        # Recent FEI evaluations
        typer.echo("\n🏷️ Recent FEI Evaluations:")
        try:
            # Get business units with recent FEI status changes
            bus = client.query_records("business_units", max_records=5)
            recent_evals = [
                bu for bu in bus
                if bu.get("fields", {}).get("FEI_Status") in ["Eligible", "Not_Eligible"]
            ][:5]
            
            if recent_evals:
                for bu in recent_evals:
                    fields = bu.get("fields", {})
                    name = fields.get("Business Unit Name", "Unknown")[:25]
                    fei_status = fields.get("FEI_Status", "Unknown")
                    emoji = "✅" if fei_status == "Eligible" else "❌"
                    typer.echo(f"   {emoji} {name:<25} → {fei_status}")
            else:
                typer.echo("   No recent evaluations")
        except Exception as e:
            typer.echo(f"   ⚠️ Could not fetch evaluations: {e}")
        
    except Exception as e:
        typer.echo(f"❌ Airtable connection failed: {e}", err=True)
        logger.error("status_airtable_error", error=str(e))
    
    typer.echo("\n" + "=" * 50)
    typer.echo("✨ Status check complete!")


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo("Alter-5 Origination Engine v0.1.0")
    typer.echo("Python wrapper for automated origination campaigns")


# ==============================================================================
# AGENT COMMANDS
# ==============================================================================


@agent_app.command("list")
def agent_list() -> None:
    """List all available AI agents."""
    agents = [
        ("Buscador_Empresas", "Search for companies matching criteria"),
        ("Enriquecedor_Datos", "Enrich company data from web sources"),
        ("Evaluador_FEI", "Evaluate FEI eligibility for companies"),
        ("Analizador_Contexto", "Analyze market context and triggers"),
        ("Selector_Targets", "Select optimal campaign targets"),
        ("Redactor_Mensajes", "Generate personalized email messages"),
    ]
    
    typer.echo("📦 Available AI Agents:\n")
    for name, description in agents:
        typer.echo(f"  • {name}")
        typer.echo(f"    {description}\n")


@agent_app.command("run")
def agent_run(
    agent_name: str = typer.Argument(..., help="Agent name to run"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without writing to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Run a specific AI agent.
    
    Available agents:
    - buscador: Search for companies
    - enriquecedor: Enrich company data
    - evaluador_fei: Evaluate FEI eligibility
    - analizador: Analyze market context
    - selector: Select campaign targets
    - redactor: Generate email messages
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    # Map short names to full agent names
    agent_map = {
        "buscador": "Buscador_Empresas",
        "enriquecedor": "Enriquecedor_Datos",
        "evaluador_fei": "Evaluador_FEI",
        "evaluador": "Evaluador_FEI",
        "analizador": "Analizador_Contexto",
        "selector": "Selector_Targets",
        "redactor": "Redactor_Mensajes",
    }
    
    normalized_name = agent_name.lower().replace("-", "_")
    full_name = agent_map.get(normalized_name, agent_name)
    
    typer.echo(f"🚀 Running agent: {full_name}")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    logger.info("agent_run_started", agent=full_name, dry_run=dry_run)
    
    # TODO: Implement actual agent execution in Sprint 1-3
    typer.echo("\n⚠️  Agent execution not yet implemented (Sprint 1+)")


# ==============================================================================
# CAMPAIGN COMMANDS
# ==============================================================================


@campaign_app.command("list")
def campaign_list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum campaigns to show"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
) -> None:
    """List origination campaigns."""
    _setup_logging(verbose)
    
    typer.echo(f"📋 Listing campaigns (limit: {limit})")
    if status:
        typer.echo(f"   Filtering by status: {status}")
    
    # TODO: Implement in Sprint 2
    typer.echo("\n⚠️  Campaign listing not yet implemented (Sprint 2+)")


@campaign_app.command("create")
def campaign_create(
    name: str = typer.Argument(..., help="Campaign name"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Campaign description"),
    priority: str = typer.Option("Medium", "--priority", "-p", help="Priority (Critical/High/Medium/Low)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without creating"),
) -> None:
    """Create a new campaign."""
    typer.echo(f"📝 Creating campaign: {name}")
    typer.echo(f"   Priority: {priority}")
    if description:
        typer.echo(f"   Description: {description}")
    if dry_run:
        typer.echo("   (dry-run mode)")
    
    # TODO: Implement in Sprint 2
    typer.echo("\n⚠️  Campaign creation not yet implemented (Sprint 2+)")


@campaign_app.command("run")
def campaign_run(
    campaign_id: str = typer.Argument(..., help="Campaign record ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without sending"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Execute a campaign (select targets and generate emails)."""
    _setup_logging(verbose)
    
    typer.echo(f"🚀 Running campaign: {campaign_id}")
    if dry_run:
        typer.echo("   (dry-run mode - no emails will be sent)")
    
    # TODO: Implement in Sprint 3
    typer.echo("\n⚠️  Campaign execution not yet implemented (Sprint 3+)")


# ==============================================================================
# COMPANY COMMANDS
# ==============================================================================


@company_app.command("search")
def company_search(
    sector: Optional[str] = typer.Option(None, "--sector", "-s", help="Target sector"),
    country: Optional[str] = typer.Option(None, "--country", "-c", help="Target country"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Search keywords (comma-separated)"),
    limit: int = typer.Option(25, "--limit", "-l", help="Maximum results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Search for companies matching criteria."""
    _setup_logging(verbose)
    
    typer.echo("🔍 Searching companies...")
    if sector:
        typer.echo(f"   Sector: {sector}")
    if country:
        typer.echo(f"   Country: {country}")
    if keywords:
        typer.echo(f"   Keywords: {keywords}")
    typer.echo(f"   Limit: {limit}")
    
    # TODO: Implement with Buscador_Empresas agent in Sprint 1
    typer.echo("\n⚠️  Company search not yet implemented (Sprint 1+)")


@company_app.command("enrich")
def company_enrich(
    company_id: str = typer.Argument(..., help="Company record ID to enrich"),
    no_financials: bool = typer.Option(False, "--no-financials", help="Skip financial data extraction"),
    no_contacts: bool = typer.Option(False, "--no-contacts", help="Skip key persons identification"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without updating"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Enrich a company's data from web sources.
    
    Uses the Enriquecedor_Datos agent to:
    - Complete basic info (employees, description, LinkedIn)
    - Extract financial data (revenue, EBITDA, debt)
    - Identify key persons (CEO, CFO, executives)
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"📊 Enriching company: {company_id}")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.enriquecedor import EnriquecedorDatos
        
        agent = EnriquecedorDatos()
        result = agent.enrich_company(
            company_id=company_id,
            include_financials=not no_financials,
            include_contacts=not no_contacts,
            dry_run=dry_run,
        )
        
        typer.echo("")
        if result.success:
            typer.echo("✅ Enrichment completed successfully!")
            
            # Show company info
            if result.company_info and result.company_info.has_data():
                typer.echo("\n📋 Company Info:")
                if result.company_info.num_employees:
                    typer.echo(f"   Employees: {result.company_info.num_employees}")
                if result.company_info.description:
                    desc = result.company_info.description[:100] + "..." if len(result.company_info.description) > 100 else result.company_info.description
                    typer.echo(f"   Description: {desc}")
                if result.company_info.linkedin_url:
                    typer.echo(f"   LinkedIn: {result.company_info.linkedin_url}")
                if result.company_info.hq_address:
                    typer.echo(f"   HQ Address: {result.company_info.hq_address}")
            
            # Show financial info
            if result.financial_info and result.financial_info.has_data():
                typer.echo("\n💰 Financial Info:")
                if result.financial_info.annual_revenues:
                    typer.echo(f"   Revenue: €{result.financial_info.annual_revenues:,.0f}")
                if result.financial_info.ebitda:
                    typer.echo(f"   EBITDA: €{result.financial_info.ebitda:,.0f}")
                if result.financial_info.year:
                    typer.echo(f"   Year: {result.financial_info.year}")
                if result.financials_created:
                    typer.echo("   ✅ Financial record created")
            
            # Show contacts
            if result.key_persons:
                typer.echo(f"\n👥 Key Persons Found: {len(result.key_persons)}")
                for person in result.key_persons[:3]:  # Show first 3
                    typer.echo(f"   • {person.first_name} {person.last_name} - {person.role}")
                if result.contacts_created > 0:
                    typer.echo(f"   ✅ {result.contacts_created} contact(s) created")
            
            typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.2f}s")
        else:
            typer.echo("❌ Enrichment failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
            raise typer.Exit(1)
            
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("enrichment_cli_error", company_id=company_id, error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@company_app.command("enrich-batch")
def company_enrich_batch(
    fei_status: str = typer.Option("Unknown", "--fei-status", "-f", help="Filter by FEI status"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum companies to process"),
    no_financials: bool = typer.Option(False, "--no-financials", help="Skip financial data extraction"),
    no_contacts: bool = typer.Option(False, "--no-contacts", help="Skip key persons identification"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without updating"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Batch enrich multiple companies.
    
    Filters companies by FEI status and enriches them in sequence.
    
    Example:
        python -m cli.main company enrich-batch --fei-status Unknown --limit 100
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo("📊 Batch Company Enrichment")
    typer.echo(f"   Filter: FEI_Status = {fei_status}")
    typer.echo(f"   Limit: {limit} companies")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.enriquecedor import EnriquecedorDatos
        from core.airtable_client import AirtableClient
        
        # Get companies to enrich
        client = AirtableClient()
        formula = f"{{FEI_Status}}='{fei_status}'"
        
        typer.echo(f"\n🔍 Querying companies with formula: {formula}")
        
        companies = client.query_records(
            table_name="companies",
            formula=formula,
            max_records=limit,
        )
        
        if not companies:
            typer.echo("⚠️  No companies found matching criteria")
            return
        
        company_ids = [c["id"] for c in companies]
        typer.echo(f"✅ Found {len(company_ids)} companies to enrich\n")
        
        # Progress callback
        def show_progress(current: int, total: int, result) -> None:
            status = "✅" if result.success else "❌"
            company_name = "Unknown"
            try:
                record = client.get_record("companies", result.company_id)
                company_name = record.get("fields", {}).get("Company Name", "Unknown")
            except Exception:
                pass
            typer.echo(f"   [{current}/{total}] {status} {company_name}")
        
        # Run batch enrichment
        agent = EnriquecedorDatos()
        
        typer.echo("🚀 Starting enrichment...")
        with typer.progressbar(length=len(company_ids), label="Enriching") as progress:
            def progress_callback(current, total, result):
                progress.update(1)
                if verbose:
                    show_progress(current, total, result)
            
            results = agent.enrich_batch(
                company_ids=company_ids,
                include_financials=not no_financials,
                include_contacts=not no_contacts,
                dry_run=dry_run,
                on_progress=progress_callback if not verbose else show_progress,
            )
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        contacts_created = sum(r.contacts_created for r in results)
        financials_created = sum(1 for r in results if r.financials_created)
        total_time = sum(r.processing_time_seconds for r in results)
        
        typer.echo("\n" + "=" * 50)
        typer.echo("📊 ENRICHMENT SUMMARY")
        typer.echo("=" * 50)
        typer.echo(f"   Total processed: {len(results)}")
        typer.echo(f"   ✅ Successful: {successful}")
        typer.echo(f"   ❌ Failed: {failed}")
        typer.echo(f"   👥 Contacts created: {contacts_created}")
        typer.echo(f"   💰 Financials created: {financials_created}")
        typer.echo(f"   ⏱️  Total time: {total_time:.2f}s")
        typer.echo(f"   📈 Avg time/company: {total_time/len(results):.2f}s")
        
        if failed > 0:
            typer.echo(f"\n⚠️  {failed} companies failed. Check logs for details.")
            
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("batch_enrichment_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# FEI COMMANDS
# ==============================================================================


@fei_app.command("evaluate")
def fei_evaluate(
    company_id: str = typer.Argument(..., help="Company record ID to evaluate"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-evaluation even if recent"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without updating"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Evaluate FEI eligibility for a company.
    
    Uses the Evaluador_FEI agent to:
    - Search for environmental certificates (ISO 14001, EMAS, etc.)
    - Find eco-labels (EU Ecolabel, FSC, etc.)
    - Identify cleantech prizes and awards
    - Analyze green business activities
    - Determine eligibility using Claude reasoning
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"🏷️  Evaluating FEI eligibility: {company_id}")
    if force:
        typer.echo("   (forcing re-evaluation)")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.evaluador_fei import EvaluadorFEI
        from core.models import FEIStatus
        
        agent = EvaluadorFEI()
        result = agent.evaluate(
            company_id=company_id,
            force=force,
            dry_run=dry_run,
        )
        
        typer.echo("")
        
        # Status indicator
        status_emoji = {
            FEIStatus.ELIGIBLE: "✅",
            FEIStatus.NOT_ELIGIBLE: "❌",
            FEIStatus.PARTIALLY_ELIGIBLE: "🟡",
            FEIStatus.PENDING_REVIEW: "🔍",
            FEIStatus.UNKNOWN: "❓",
            FEIStatus.EXPIRED: "⏰",
        }
        
        emoji = status_emoji.get(result.status, "❓")
        typer.echo(f"{emoji} FEI Status: {result.status.value}")
        typer.echo(f"📊 Confidence: {result.confidence:.0f}%")
        
        if result.criteria_met:
            typer.echo(f"\n✅ Criteria Met:")
            for criterion in result.criteria_met:
                typer.echo(f"   • {criterion.value}")
        
        # Show evidence found
        if result.certificates_found:
            typer.echo(f"\n📜 Certificates Found: {len(result.certificates_found)}")
            for cert in result.certificates_found[:3]:
                typer.echo(f"   • {cert.certificate_name}")
        
        if result.prizes_found:
            typer.echo(f"\n🏆 Prizes Found: {len(result.prizes_found)}")
            for prize in result.prizes_found[:3]:
                typer.echo(f"   • {prize.prize_name} ({prize.year or 'N/A'})")
        
        if result.green_activities:
            typer.echo(f"\n🌱 Green Activities: {len(result.green_activities)}")
            for activity in result.green_activities[:3]:
                pct = f"{activity.revenue_percentage:.0f}%" if activity.revenue_percentage else "N/A"
                typer.echo(f"   • {activity.activity_name}: {pct}")
        
        # Reasoning
        if verbose and result.reasoning:
            typer.echo(f"\n📝 Reasoning:")
            # Truncate for display
            reasoning = result.reasoning[:500] + "..." if len(result.reasoning) > 500 else result.reasoning
            typer.echo(f"   {reasoning}")
        
        typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.2f}s")
        
        if result.errors:
            typer.echo("\n⚠️  Warnings:")
            for error in result.errors:
                typer.echo(f"   {error}", err=True)
                
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("fei_evaluate_cli_error", company_id=company_id, error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@fei_app.command("batch")
def fei_batch(
    status_filter: str = typer.Option("Unknown", "--status", "-s", help="Filter by current FEI status"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum companies to evaluate"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-evaluation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without updating"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Batch evaluate FEI eligibility for multiple companies.
    
    Example:
        python -m cli.main fei batch --status Unknown --limit 200
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"🏷️  Batch FEI Evaluation")
    typer.echo(f"   Filter: FEI_Status = {status_filter}")
    typer.echo(f"   Limit: {limit} companies")
    if force:
        typer.echo("   (forcing re-evaluation)")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.evaluador_fei import EvaluadorFEI
        from core.airtable_client import AirtableClient
        from core.models import FEIStatus
        
        # Get companies to evaluate
        client = AirtableClient()
        formula = f"{{FEI_Status}}='{status_filter}'"
        
        typer.echo(f"\n🔍 Querying companies with formula: {formula}")
        
        companies = client.query_records(
            table_name="companies",
            formula=formula,
            max_records=limit,
        )
        
        if not companies:
            typer.echo("⚠️  No companies found matching criteria")
            return
        
        company_ids = [c["id"] for c in companies]
        typer.echo(f"✅ Found {len(company_ids)} companies to evaluate\n")
        
        # Progress callback
        def show_progress(current: int, total: int, result) -> None:
            status_emoji = {
                FEIStatus.ELIGIBLE: "✅",
                FEIStatus.NOT_ELIGIBLE: "❌",
                FEIStatus.PARTIALLY_ELIGIBLE: "🟡",
                FEIStatus.PENDING_REVIEW: "🔍",
                FEIStatus.UNKNOWN: "❓",
            }
            emoji = status_emoji.get(result.status, "❓")
            name = result.company_name[:30] + "..." if len(result.company_name) > 30 else result.company_name
            typer.echo(f"   [{current}/{total}] {emoji} {name}: {result.status.value} ({result.confidence:.0f}%)")
        
        # Run batch evaluation
        agent = EvaluadorFEI()
        
        typer.echo("🚀 Starting FEI evaluation...")
        results = agent.evaluate_batch(
            company_ids=company_ids,
            force=force,
            dry_run=dry_run,
            on_progress=show_progress if verbose else None,
        )
        
        # Summary
        eligible = sum(1 for r in results if r.status == FEIStatus.ELIGIBLE)
        not_eligible = sum(1 for r in results if r.status == FEIStatus.NOT_ELIGIBLE)
        partial = sum(1 for r in results if r.status == FEIStatus.PARTIALLY_ELIGIBLE)
        pending = sum(1 for r in results if r.status == FEIStatus.PENDING_REVIEW)
        unknown = sum(1 for r in results if r.status == FEIStatus.UNKNOWN)
        avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0
        total_time = sum(r.processing_time_seconds for r in results)
        
        typer.echo("\n" + "=" * 50)
        typer.echo("📊 FEI EVALUATION SUMMARY")
        typer.echo("=" * 50)
        typer.echo(f"   Total processed: {len(results)}")
        typer.echo(f"   ✅ Eligible: {eligible}")
        typer.echo(f"   ❌ Not Eligible: {not_eligible}")
        typer.echo(f"   🟡 Partially Eligible: {partial}")
        typer.echo(f"   🔍 Pending Review: {pending}")
        typer.echo(f"   ❓ Unknown: {unknown}")
        typer.echo(f"   📈 Average Confidence: {avg_confidence:.0f}%")
        typer.echo(f"   ⏱️  Total time: {total_time:.2f}s")
        typer.echo(f"   📈 Avg time/company: {total_time/len(results):.2f}s")
        
        # Eligibility rate
        if len(results) > 0:
            eligibility_rate = (eligible / len(results)) * 100
            typer.echo(f"\n   🎯 Eligibility Rate: {eligibility_rate:.1f}%")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("fei_batch_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@fei_app.command("stats")
def fei_stats(verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed stats")) -> None:
    """Show FEI eligibility statistics."""
    _setup_logging(verbose)
    
    typer.echo("📊 FEI Eligibility Statistics\n")
    
    # TODO: Query Airtable for actual stats
    typer.echo("⚠️  Statistics not yet implemented (Sprint 1+)")


# ==============================================================================
# CONTEXT COMMANDS (Agent 4: AnalizadorContexto)
# ==============================================================================


@context_app.command("analyze")
def context_analyze(
    trigger: str = typer.Argument(..., help="Market trigger or news to analyze"),
    sectors: Optional[str] = typer.Option(None, "--sectors", "-s", help="Comma-separated target sectors"),
    countries: Optional[str] = typer.Option(None, "--countries", "-c", help="Comma-separated target countries"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't save to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Analyze a market trigger for campaign opportunities.
    
    Uses the Analizador_Contexto agent to:
    - Search related news with Gemini
    - Analyze market impact with Claude
    - Generate communication angles
    - Evaluate campaign potential
    
    Example:
        python -m cli.main context analyze "BCE baja tipos 0.25%" --sectors Industrials,Renewables
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"🔍 Analyzing market trigger: {trigger[:50]}...")
    if sectors:
        typer.echo(f"   Target sectors: {sectors}")
    if countries:
        typer.echo(f"   Target countries: {countries}")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.analizador import AnalizadorContexto
        
        # Parse optional parameters
        target_sectors = [s.strip() for s in sectors.split(",")] if sectors else None
        target_countries = [c.strip() for c in countries.split(",")] if countries else None
        
        agent = AnalizadorContexto()
        result = agent.analyze(
            trigger=trigger,
            target_sectors=target_sectors,
            target_countries=target_countries,
            dry_run=dry_run,
        )
        
        typer.echo("")
        
        if result.success:
            typer.echo("✅ Analysis completed successfully!")
            
            # Show news found
            if result.news_found:
                typer.echo(f"\n📰 News Found: {len(result.news_found)}")
                for news in result.news_found[:5]:
                    score = f" ({news.relevance_score:.0%})" if news.relevance_score else ""
                    typer.echo(f"   • {news.title[:60]}...{score}")
            
            # Show impact analysis
            if result.impact:
                impact = result.impact
                typer.echo(f"\n📊 Impact Analysis:")
                typer.echo(f"   Urgency: {impact.urgency.value}")
                typer.echo(f"   Campaign Potential: {impact.campaign_potential}/5")
                if impact.affected_sectors:
                    typer.echo(f"   Sectors: {', '.join(impact.affected_sectors)}")
                if impact.affected_countries:
                    typer.echo(f"   Countries: {', '.join(impact.affected_countries)}")
                if impact.recommended_product:
                    typer.echo(f"   Recommended Product: {impact.recommended_product}")
            
            # Show key angles
            if result.key_angles:
                typer.echo(f"\n💡 Key Communication Angles:")
                for i, angle in enumerate(result.key_angles[:5], 1):
                    typer.echo(f"   {i}. {angle}")
            
            # Campaign recommendation
            if result.should_create_campaign():
                typer.echo(f"\n🚀 Recommendation: CREATE CAMPAIGN")
            else:
                typer.echo(f"\n⚠️  Recommendation: Low campaign potential")
            
            if result.market_context_id:
                typer.echo(f"\n📝 Market Context saved: {result.market_context_id}")
        else:
            typer.echo("❌ Analysis failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
        typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.2f}s")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("context_analyze_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# CAMPAIGN SELECTION COMMANDS (Agent 5: SelectorTargets)
# ==============================================================================


@campaign_app.command("select")
def campaign_select(
    campaign_id: str = typer.Argument(..., help="Campaign record ID"),
    sectors: str = typer.Option(..., "--sectors", "-s", help="Comma-separated sectors to target"),
    countries: str = typer.Option(..., "--countries", "-c", help="Comma-separated countries to target"),
    max_targets: int = typer.Option(30, "--max", "-m", help="Maximum targets to select"),
    min_score: float = typer.Option(0.6, "--min-score", help="Minimum fit score (0-1)"),
    include_cooling: bool = typer.Option(False, "--include-cooling", help="Include companies in cooling-off"),
    context: Optional[str] = typer.Option(None, "--context", help="Market context for justifications"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't save to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Select targets for a campaign.
    
    Uses the Selector_Targets agent to:
    - Filter Business Units by criteria
    - Apply cooling-off period (90 days)
    - Calculate fit scores
    - Prioritize targets
    - Generate selection justifications
    
    Example:
        python -m cli.main campaign select recCampXXX --sectors Industrials,Renewables --countries ES,PT
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"🎯 Selecting targets for campaign: {campaign_id}")
    typer.echo(f"   Sectors: {sectors}")
    typer.echo(f"   Countries: {countries}")
    typer.echo(f"   Max targets: {max_targets}")
    typer.echo(f"   Min fit score: {min_score:.0%}")
    if include_cooling:
        typer.echo("   (including companies in cooling-off)")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.selector import SelectorTargets
        
        target_sectors = [s.strip() for s in sectors.split(",")]
        target_countries = [c.strip() for c in countries.split(",")]
        
        agent = SelectorTargets()
        result = agent.select(
            campaign_id=campaign_id,
            affected_sectors=target_sectors,
            affected_countries=target_countries,
            market_context_summary=context,
            max_targets=max_targets,
            min_fit_score=min_score,
            include_cooling_off=include_cooling,
            dry_run=dry_run,
        )
        
        typer.echo("")
        
        if result.success:
            typer.echo("✅ Selection completed successfully!")
            typer.echo(f"\n📊 Selection Summary:")
            typer.echo(f"   Total candidates: {result.total_candidates}")
            typer.echo(f"   Selected: {len(result.targets)}")
            typer.echo(f"   Excluded (cooling-off): {result.excluded_cooling_off}")
            typer.echo(f"   Excluded (low score): {result.excluded_low_score}")
            
            if result.targets:
                avg_score = sum(t.fit_score for t in result.targets) / len(result.targets)
                typer.echo(f"   Average fit score: {avg_score:.0%}")
                
                typer.echo(f"\n🎯 Selected Targets:")
                for i, target in enumerate(result.targets[:10], 1):
                    fei = "✓" if target.fei_status == "Eligible" else ""
                    key = "👤" if target.has_key_person else ""
                    typer.echo(f"   {i}. {target.company_name} ({target.business_unit_name})")
                    typer.echo(f"      Score: {target.fit_score:.0%} {fei} {key}")
                    if verbose and target.selection_justification:
                        typer.echo(f"      {target.selection_justification[:80]}...")
                
                if len(result.targets) > 10:
                    typer.echo(f"   ... and {len(result.targets) - 10} more")
        else:
            typer.echo("❌ Selection failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
        typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.2f}s")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("campaign_select_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# MESSAGE COMMANDS (Agent 6: RedactorMensajes)
# ==============================================================================


@message_app.command("generate")
def message_generate(
    target_id: str = typer.Argument(..., help="Campaign target record ID"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Campaign context"),
    tone: str = typer.Option("professional", "--tone", "-t", help="Message tone"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't save to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Generate a personalized email for a campaign target.
    
    Uses the Redactor_Mensajes agent to:
    - Load target and company context
    - Generate personalized subject line
    - Create message body (max 150 words)
    - Calculate personalization score
    
    Example:
        python -m cli.main message generate recTargetXXX --tone professional
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"✉️  Generating message for target: {target_id}")
    typer.echo(f"   Tone: {tone}")
    if context:
        typer.echo(f"   Context: {context[:50]}...")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.redactor import RedactorMensajes, MAX_EMAIL_WORDS
        
        agent = RedactorMensajes()
        result = agent.generate(
            target_id=target_id,
            campaign_context=context,
            tone=tone,
            dry_run=dry_run,
        )
        
        typer.echo("")
        
        if result.success and result.message:
            msg = result.message
            typer.echo("✅ Message generated successfully!")
            
            typer.echo(f"\n📧 Subject: {msg.subject}")
            typer.echo(f"\n📝 Body ({msg.word_count}/{MAX_EMAIL_WORDS} words):")
            typer.echo("-" * 50)
            typer.echo(msg.body)
            typer.echo("-" * 50)
            
            typer.echo(f"\n📊 Metrics:")
            typer.echo(f"   Personalization: {msg.personalization_score:.0%}")
            typer.echo(f"   Word count: {msg.word_count}")
            typer.echo(f"   Within limits: {'✅' if msg.is_within_limits() else '❌'}")
            
            if msg.cta:
                typer.echo(f"   CTA: {msg.cta}")
            
            if result.warnings:
                typer.echo("\n⚠️  Warnings:")
                for warning in result.warnings:
                    typer.echo(f"   {warning}")
        else:
            typer.echo("❌ Message generation failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
        typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.2f}s")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("message_generate_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@message_app.command("batch")
def message_batch(
    campaign_id: str = typer.Argument(..., help="Campaign record ID"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Campaign context"),
    tone: str = typer.Option("professional", "--tone", "-t", help="Message tone"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't save to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Generate messages for all targets in a campaign.
    
    Example:
        python -m cli.main message batch recCampXXX --tone professional
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo(f"✉️  Batch message generation for campaign: {campaign_id}")
    typer.echo(f"   Tone: {tone}")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    
    try:
        from agents.redactor import RedactorMensajes
        
        agent = RedactorMensajes()
        result = agent.generate_batch(
            campaign_id=campaign_id,
            campaign_context=context,
            tone=tone,
            dry_run=dry_run,
        )
        
        typer.echo("")
        typer.echo("=" * 50)
        typer.echo("📊 BATCH GENERATION SUMMARY")
        typer.echo("=" * 50)
        typer.echo(f"   Campaign: {campaign_id}")
        typer.echo(f"   Total targets: {len(result.results)}")
        typer.echo(f"   ✅ Successful: {result.success_count}")
        typer.echo(f"   ❌ Failed: {result.failure_count}")
        
        if result.results:
            successful_results = [r for r in result.results if r.success and r.message]
            if successful_results:
                avg_words = sum(r.message.word_count for r in successful_results) / len(successful_results)
                avg_pers = sum(r.message.personalization_score for r in successful_results) / len(successful_results)
                typer.echo(f"   📈 Avg words: {avg_words:.0f}")
                typer.echo(f"   📈 Avg personalization: {avg_pers:.0%}")
        
        typer.echo(f"   ⏱️  Total time: {result.total_processing_time_seconds:.2f}s")
        
        if verbose and result.failure_count > 0:
            typer.echo("\n❌ Failed targets:")
            for r in result.results:
                if not r.success:
                    typer.echo(f"   {r.target_id}: {', '.join(r.errors)}")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("message_batch_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# CAMPAIGN ORCHESTRATION COMMANDS
# ==============================================================================


@campaign_app.command("create")
def campaign_create(
    trigger: str = typer.Argument(..., help="Market trigger to analyze"),
    sectors: str = typer.Option(..., "--sectors", "-s", help="Comma-separated sectors"),
    countries: str = typer.Option(..., "--countries", "-c", help="Comma-separated countries"),
    max_targets: int = typer.Option(30, "--max", "-m", help="Maximum targets"),
    min_score: float = typer.Option(0.6, "--min-score", help="Minimum fit score"),
    tone: str = typer.Option("professional", "--tone", "-t", help="Email tone"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Auto-approve targets"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't save to Airtable"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Create a full campaign from a market trigger.
    
    This command runs the complete campaign creation flow:
    1. Analyzes the trigger with AnalizadorContexto
    2. Selects best targets with SelectorTargets
    3. Waits for approval (or auto-approves with --auto-approve)
    4. Generates personalized emails with RedactorMensajes
    
    Example:
        python -m cli.main campaign create "BCE baja tipos 0.25%" \\
            --sectors Industrials,Renewables \\
            --countries ES,PT \\
            --max 20 --auto-approve
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo("🚀 Creating Campaign from Trigger")
    typer.echo("=" * 50)
    typer.echo(f"   Trigger: {trigger[:60]}...")
    typer.echo(f"   Sectors: {sectors}")
    typer.echo(f"   Countries: {countries}")
    typer.echo(f"   Max Targets: {max_targets}")
    typer.echo(f"   Min Score: {min_score:.0%}")
    typer.echo(f"   Tone: {tone}")
    if auto_approve:
        typer.echo("   ✅ Auto-approve enabled")
    if dry_run:
        typer.echo("   (dry-run mode - no changes will be saved)")
    typer.echo("")
    
    try:
        from core.campaign_orchestrator import CampaignOrchestrator
        
        target_sectors = [s.strip() for s in sectors.split(",")]
        target_countries = [c.strip() for c in countries.split(",")]
        
        orchestrator = CampaignOrchestrator()
        
        # Step 1: Create proposal
        typer.echo("📊 Step 1: Analyzing trigger...")
        proposal = orchestrator.create_proposal(
            trigger=trigger,
            sectors=target_sectors,
            countries=target_countries,
            max_targets=max_targets,
            min_fit_score=min_score,
            dry_run=dry_run,
        )
        
        typer.echo(f"   Status: {proposal.status}")
        
        if proposal.analysis and proposal.analysis.success:
            impact = proposal.analysis.impact
            if impact:
                typer.echo(f"   Campaign Potential: {impact.campaign_potential}/5")
                typer.echo(f"   Urgency: {impact.urgency.value}")
        
        if proposal.status not in ["Pending_Approval"]:
            typer.echo(f"\n❌ Proposal failed: {proposal.status}")
            if proposal.analysis and proposal.analysis.errors:
                for error in proposal.analysis.errors:
                    typer.echo(f"   Error: {error}", err=True)
            raise typer.Exit(1)
        
        # Show targets
        if proposal.selection and proposal.selection.targets:
            targets = proposal.selection.targets
            typer.echo(f"\n🎯 Step 2: {len(targets)} targets selected")
            
            for i, target in enumerate(targets[:10], 1):
                fei = "✓FEI" if target.fei_status == "Eligible" else ""
                typer.echo(f"   {i}. {target.company_name} - {target.fit_score:.0%} {fei}")
            
            if len(targets) > 10:
                typer.echo(f"   ... and {len(targets) - 10} more")
            
            avg_score = sum(t.fit_score for t in targets) / len(targets)
            typer.echo(f"\n   Average Fit Score: {avg_score:.0%}")
            typer.echo(f"   Excluded (cooling-off): {proposal.selection.excluded_cooling_off}")
            typer.echo(f"   Excluded (low score): {proposal.selection.excluded_low_score}")
        
        # Step 3: Approval
        if not auto_approve:
            typer.echo("\n⏸️  Step 3: Waiting for approval...")
            approved = typer.confirm("Do you want to proceed with these targets?")
            if not approved:
                typer.echo("❌ Campaign cancelled by user")
                raise typer.Exit(0)
        else:
            typer.echo("\n✅ Step 3: Auto-approved")
        
        orchestrator.approve_campaign(proposal.campaign_id, dry_run)
        
        # Step 4: Generate messages
        typer.echo("\n✉️  Step 4: Generating messages...")
        
        key_angles = proposal.analysis.key_angles if proposal.analysis else None
        result = orchestrator.complete_campaign(
            campaign_id=proposal.campaign_id,
            campaign_context=trigger,
            key_angles=key_angles,
            tone=tone,
            dry_run=dry_run,
        )
        
        # Summary
        typer.echo("\n" + "=" * 50)
        typer.echo("📊 CAMPAIGN SUMMARY")
        typer.echo("=" * 50)
        typer.echo(f"   Campaign ID: {proposal.campaign_id}")
        typer.echo(f"   Status: {result.status}")
        
        if result.messages:
            typer.echo(f"   ✅ Messages Generated: {result.messages.success_count}")
            typer.echo(f"   ❌ Messages Failed: {result.messages.failure_count}")
        
        typer.echo(f"   ⏱️  Total Time: {result.total_processing_time_seconds:.1f}s")
        
        if result.success:
            typer.echo("\n🎉 Campaign created successfully!")
        else:
            typer.echo("\n⚠️  Campaign completed with errors")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load modules: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("campaign_create_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# SEARCH COMMANDS (Agent 1: BuscadorEmpresas)
# ==============================================================================


@search_app.command("companies")
def search_companies(
    sector: str = typer.Option(..., "--sector", "-s", help="Target sector"),
    country: str = typer.Option("ES", "--country", "-c", help="Target country code"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Target region"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords"),
    min_employees: Optional[int] = typer.Option(None, "--min-employees", help="Minimum employees"),
    limit: int = typer.Option(25, "--limit", "-l", help="Maximum companies to find"),
    verify_urls: bool = typer.Option(True, "--verify/--no-verify", help="Verify URLs"),
    create: bool = typer.Option(False, "--create", help="Create records in Airtable"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't create records"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Search for new companies matching criteria.
    
    Uses the Buscador_Empresas agent to find companies using Gemini search.
    
    Example:
        python -m cli.main search companies --sector renovables --country ES --region Andalucía
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo("🔍 Searching for Companies")
    typer.echo("=" * 50)
    typer.echo(f"   Sector: {sector}")
    typer.echo(f"   Country: {country}")
    if region:
        typer.echo(f"   Region: {region}")
    if keywords:
        typer.echo(f"   Keywords: {keywords}")
    if min_employees:
        typer.echo(f"   Min Employees: {min_employees}")
    typer.echo(f"   Limit: {limit}")
    typer.echo(f"   Verify URLs: {verify_urls}")
    if dry_run:
        typer.echo("   (dry-run mode - no records will be created)")
    typer.echo("")
    
    try:
        from agents.buscador import BuscadorEmpresas
        
        kw_list = [k.strip() for k in keywords.split(",")] if keywords else None
        
        agent = BuscadorEmpresas()
        
        typer.echo("🔎 Searching with Gemini...")
        result = agent.search(
            sector=sector,
            country=country,
            region=region,
            keywords=kw_list,
            min_employees=min_employees,
            limit=limit,
            verify_urls=verify_urls,
            deduplicate=True,
            create_records=create and not dry_run,
            dry_run=dry_run,
        )
        
        typer.echo("")
        
        if result.success:
            typer.echo("✅ Search completed!")
            typer.echo(f"\n📊 Results:")
            typer.echo(f"   Found: {len(result.candidates_found)} candidates")
            typer.echo(f"   Verified URLs: {result.candidates_verified}")
            typer.echo(f"   Duplicates: {result.duplicates_found}")
            
            if result.candidates_found:
                typer.echo(f"\n📋 Companies Found:")
                
                for i, candidate in enumerate(result.candidates_found[:20], 1):
                    status = ""
                    if candidate.is_duplicate:
                        status = "⚠️ DUPLICATE"
                    elif not candidate.url_verified:
                        status = "❌ URL Failed"
                    else:
                        status = "✅"
                    
                    typer.echo(f"   {i}. {candidate.name}")
                    typer.echo(f"      {candidate.home_url or 'No URL'} {status}")
                    if verbose and candidate.description:
                        typer.echo(f"      {candidate.description[:60]}...")
                
                if len(result.candidates_found) > 20:
                    typer.echo(f"   ... and {len(result.candidates_found) - 20} more")
            
            # Ask for confirmation to create if not already creating
            if not create and not dry_run and result.get_new_candidates():
                typer.echo(f"\n{len(result.get_new_candidates())} new companies ready to create.")
                if typer.confirm("Create records in Airtable?"):
                    typer.echo("\n💾 Creating records...")
                    # Re-run with create=True
                    result = agent.search(
                        sector=sector,
                        country=country,
                        region=region,
                        keywords=kw_list,
                        min_employees=min_employees,
                        limit=limit,
                        verify_urls=False,  # Already verified
                        deduplicate=False,  # Already deduplicated
                        create_records=True,
                    )
                    typer.echo(f"   ✅ Created {result.candidates_created} companies")
            
            if result.candidates_created > 0:
                typer.echo(f"\n💾 Created: {result.candidates_created} companies")
        else:
            typer.echo("❌ Search failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
        typer.echo(f"\n⏱️  Processing time: {result.processing_time_seconds:.1f}s")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load agent: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("search_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# ORIGINATION PIPELINE COMMANDS
# ==============================================================================


@app.command("originate")
def originate_pipeline(
    sector: str = typer.Option(..., "--sector", "-s", help="Target sector"),
    country: str = typer.Option("ES", "--country", "-c", help="Target country code"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Target region"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords"),
    min_employees: Optional[int] = typer.Option(None, "--min-employees", help="Minimum employees"),
    limit: int = typer.Option(25, "--limit", "-l", help="Maximum companies"),
    enrich: bool = typer.Option(True, "--enrich/--no-enrich", help="Run enrichment"),
    evaluate_fei: bool = typer.Option(True, "--fei/--no-fei", help="Evaluate FEI"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't create/update records"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Run the full origination pipeline: Search → Enrich → Evaluate FEI.
    
    This command orchestrates agents 1, 2, and 3 to:
    1. Find new companies matching criteria (Buscador)
    2. Enrich company data from web sources (Enriquecedor)
    3. Evaluate FEI eligibility (Evaluador)
    
    Example:
        python -m cli.main originate --sector renovables --country ES --limit 10
    """
    _setup_logging(verbose)
    logger = get_logger()
    
    typer.echo("🚀 Origination Pipeline")
    typer.echo("=" * 50)
    typer.echo(f"   Sector: {sector}")
    typer.echo(f"   Country: {country}")
    if region:
        typer.echo(f"   Region: {region}")
    typer.echo(f"   Limit: {limit}")
    typer.echo(f"   Enrich: {'✅' if enrich else '❌'}")
    typer.echo(f"   Evaluate FEI: {'✅' if evaluate_fei else '❌'}")
    if dry_run:
        typer.echo("   (dry-run mode - no records will be created)")
    typer.echo("")
    
    try:
        from core.origination_pipeline import OriginationPipeline
        
        kw_list = [k.strip() for k in keywords.split(",")] if keywords else None
        
        def progress_callback(step: int, total: int, message: str) -> None:
            phases = {0: "🔍", 1: "📊", 2: "🏷️", 3: "✅"}
            typer.echo(f"{phases.get(step, '▶️')} Step {step + 1}/{total}: {message}")
        
        pipeline = OriginationPipeline()
        
        result = pipeline.originate(
            sector=sector,
            country=country,
            region=region,
            keywords=kw_list,
            min_employees=min_employees,
            limit=limit,
            enrich=enrich,
            evaluate_fei=evaluate_fei,
            on_progress=progress_callback,
            dry_run=dry_run,
        )
        
        typer.echo("")
        typer.echo("=" * 50)
        typer.echo("📊 ORIGINATION SUMMARY")
        typer.echo("=" * 50)
        
        if result.success:
            typer.echo(f"   ✅ Pipeline completed successfully!")
            typer.echo(f"\n   Companies Found: {result.companies_found}")
            typer.echo(f"   Companies Enriched: {result.companies_enriched}")
            typer.echo(f"   FEI Evaluated: {result.companies_fei_evaluated}")
            typer.echo(f"   FEI Eligible: {result.companies_fei_eligible}")
            
            # Show eligible companies
            eligible = result.get_eligible_companies()
            if eligible:
                typer.echo(f"\n🏆 FEI Eligible Companies ({len(eligible)}):")
                for company in eligible[:10]:
                    typer.echo(f"   ✅ {company.company_name}")
                if len(eligible) > 10:
                    typer.echo(f"   ... and {len(eligible) - 10} more")
            
            # Show detailed results if verbose
            if verbose and result.company_results:
                typer.echo(f"\n📋 All Results:")
                for company in result.company_results[:20]:
                    typer.echo(f"   {company.summary()}")
        else:
            typer.echo("❌ Pipeline failed!")
            for error in result.errors:
                typer.echo(f"   Error: {error}", err=True)
        
        typer.echo(f"\n⏱️  Total time: {result.total_processing_time_seconds:.1f}s")
        
    except ImportError as e:
        typer.echo(f"❌ Failed to load pipeline: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error("originate_cli_error", error=str(e), exc_info=True)
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


# ==============================================================================
# ENTRY POINT
# ==============================================================================


def main() -> None:
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()

