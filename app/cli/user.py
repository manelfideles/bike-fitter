import typer

from app.db import SessionLocal
from app.models.user import User

app = typer.Typer()


@app.command("create")
def create_user(
    name: str,
    height_cm: float,
    weight_kg: float = typer.Option(None),
    inseam_cm: float = typer.Option(...),
    torso_cm: float = typer.Option(...),
    arm_cm: float = typer.Option(...),
    shoulder_cm: float = typer.Option(...),
    riding_position: str = typer.Option(..., help="aero | sport | comfort"),
):
    db = SessionLocal()
    user = User(
        name=name,
        height_cm=height_cm,
        weight_kg=weight_kg,
        inseam_cm=inseam_cm,
        torso_cm=torso_cm,
        arm_cm=arm_cm,
        shoulder_cm=shoulder_cm,
        riding_position=riding_position.lower(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    typer.echo(f"✅ Created user with ID {user.id}")
    db.close()


@app.command("list")
def list_users():
    """List all registered users."""
    db = SessionLocal()
    users = db.query(User).all()
    if not users:
        typer.echo("No users found.")
        return

    for user in users:
        typer.echo(
            f"[{user.id}] {user.name} - {user.height_cm} cm, "
            f"{user.weight_kg or 'N/A'} kg, "
            f"{user.riding_position.title()} rider"
        )
    db.close()


@app.command("edit")
def edit_user(
    user_id: int = typer.Option(..., help="ID of the user to edit"),
    name: str = typer.Option(None),
    weight: float = typer.Option(None),
    height: float = typer.Option(None),
    inseam: float = typer.Option(None),
    torso: float = typer.Option(None),
    arm: float = typer.Option(None),
    shoulder_width: float = typer.Option(None),
    preferred_position: str = typer.Option(None),
):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        typer.echo("❌ User not found.")
        raise typer.Exit()

    updated = False
    for field, value in {
        "name": name,
        "weight": weight,
        "height": height,
        "inseam": inseam,
        "torso": torso,
        "arm": arm,
        "shoulder_width": shoulder_width,
        "preferred_position": preferred_position,
    }.items():
        if value is not None:
            setattr(user, field, value)
            updated = True

    if updated:
        db.commit()
        typer.echo("✅ User updated.")
    else:
        typer.echo("ℹ️ No fields to update.")
