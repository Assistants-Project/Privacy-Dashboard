import click
import traceback
from flask.cli import with_appcontext
from .extensions import db
from .models import User
from .services.owl_service import OWLService

@click.command("generate-owls")
@click.option("--force", is_flag=True, help="Overwrite existing OWL files.")
@with_appcontext
def generate_owls_command(force):
    """Generates missing OWL files for existing Smart Homes."""
    from .models.entities.smart_home import SmartHome
    import os
    
    homes = db.session.execute(db.select(SmartHome)).scalars().all()
    
    if not homes:
        click.echo("No Smart Homes found.")
        return

    click.echo(f"Checking {len(homes)} homes for missing OWL files...")
    
    count = 0
    ontology_dir = OWLService._get_ontology_dir()
    homes_dir = os.path.join(ontology_dir, "homes")
    
    for home in homes:
        try:
            # Check if file exists
            filename = f"{home.uuid}.owl"
            path = os.path.join(homes_dir, filename)
            
            if os.path.exists(path) and not force:
                click.echo(f"Skipping {home.name} ({home.uuid}) - already exists (use --force to overwrite).")
                continue
                
            click.echo(f"Generating OWL for home {home.name} ({home.uuid})...")
            OWLService.create_home_ontology(home.uuid)
            count += 1
        except Exception as e:
            click.echo(f"Error generating OWL for home {home.uuid}: {e}")
            click.echo("Full traceback:")
            traceback.print_exc()
    
    click.echo(f"Successfully generated {count} OWL files.")
