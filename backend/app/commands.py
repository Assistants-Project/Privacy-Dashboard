import click
import traceback
from flask.cli import with_appcontext
from .extensions import db
from .models import User
from .services.owl_service import OWLService

@click.command("generate-owls")
@with_appcontext
def generate_owls_command():
    """Generates missing OWL files for existing users."""
    users = db.session.execute(db.select(User).where(User.ontology_iri == None)).scalars().all()
    
    if not users:
        click.echo("No users found without OWL files.")
        return

    click.echo(f"Found {len(users)} users without OWL files. Generating...")
    
    count = 0
    for user in users:
        try:
            click.echo(f"Generating OWL for user {user.email} ({user.uuid})...")
            iri = OWLService.create_user_ontology(user.uuid)
            user.ontology_iri = iri
            count += 1
        except Exception as e:
            click.echo(f"Error generating OWL for user {user.uuid}: {e}")
            click.echo("Full traceback:")
            traceback.print_exc()
    
    db.session.commit()
    click.echo(f"Successfully generated {count} OWL files.")
