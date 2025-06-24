import typer

from app.db import SessionLocal
from app.models.bike import Bike

app = typer.Typer()


@app.command("create")
def create_bike(
    user_id: int,
    brand: str,
    model: str,
    weight_kg: float = typer.Option(None),
    stack: float = typer.Option(...),
    reach: float = typer.Option(...),
    top_tube_length: float = typer.Option(...),
    seat_tube_angle: float = typer.Option(...),
    head_tube_angle: float = typer.Option(...),
    seat_height: float = typer.Option(...),
    saddle_setback: float = typer.Option(...),
    stem_length: float = typer.Option(...),
    handlebar_width: float = typer.Option(...),
    crank_length: float = typer.Option(...),
):
    db = SessionLocal()
    bike = Bike(
        user_id=user_id,
        brand=brand,
        model=model,
        weight_kg=weight_kg,
        stack=stack,
        reach=reach,
        top_tube_length=top_tube_length,
        seat_tube_angle=seat_tube_angle,
        head_tube_angle=head_tube_angle,
        seat_height=seat_height,
        saddle_setback=saddle_setback,
        stem_length=stem_length,
        handlebar_width=handlebar_width,
        crank_length=crank_length,
    )
    db.add(bike)
    db.commit()
    db.refresh(bike)
    typer.echo(f"🚴 Created bike with ID {bike.id} for user {user_id}")
    db.close()


@app.command("list")
def list_bikes(user_id: int = typer.Option(None, help="Filter by user ID")):
    """List all bikes, optionally by user."""
    db = SessionLocal()
    query = db.query(Bike)
    if user_id:
        query = query.filter(Bike.user_id == user_id)

    bikes = query.all()
    if not bikes:
        typer.echo("No bikes found.")
        return

    for bike in bikes:
        typer.echo(
            f"[{bike.id}] {bike.brand} {bike.model} (User {bike.user_id}): \n"
            f"    Stack (mm): {bike.stack}\n"
            f"    Reach (mm): {bike.reach}\n"
            f"    Top Tube Length (mm): {bike.top_tube_length}\n"
            f"    Seat Tube Angle (degrees): {bike.seat_tube_angle}\n"
            f"    Head Tube Angle (degrees): {bike.head_tube_angle}\n"
            f"    Seat Height (mm): {bike.seat_height}\n"
            f"    Saddle Setback (mm): {bike.saddle_setback}\n"
            f"    Stem Length (mm): {bike.stem_length}\n"
            f"    Handlebar Width (mm): {bike.handlebar_width}\n"
            f"    Crank Length (mm): {bike.crank_length}"
        )
    db.close()


@app.command("edit")
def edit_bike(
    bike_id: int = typer.Option(..., help="ID of the bike to edit"),
    brand: str = typer.Option(None),
    model: str = typer.Option(None),
    saddle_height: float = typer.Option(None),
    saddle_setback: float = typer.Option(None),
    reach: float = typer.Option(None),
    stack: float = typer.Option(None),
    handlebar_height: float = typer.Option(None),
    crank_length: float = typer.Option(None),
    weight: float = typer.Option(None),
):
    db = SessionLocal()
    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        typer.echo("❌ Bike not found.")
        raise typer.Exit()

    updated = False
    for field, value in {
        "brand": brand,
        "model": model,
        "saddle_height": saddle_height,
        "saddle_setback": saddle_setback,
        "reach": reach,
        "stack": stack,
        "handlebar_height": handlebar_height,
        "crank_length": crank_length,
        "weight": weight,
    }.items():
        if value is not None:
            setattr(bike, field, value)
            updated = True

    if updated:
        db.commit()
        typer.echo("✅ Bike updated.")
    else:
        typer.echo("ℹ️ No fields to update.")
