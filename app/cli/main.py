import typer

from app.cli import bike, fit, user

app = typer.Typer()
app.add_typer(user.app, name="user")
app.add_typer(bike.app, name="bike")
app.add_typer(fit.app, name="fit")

if __name__ == "__main__":
    app()
