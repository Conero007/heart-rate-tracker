from website import create_app
import heart_rate_monitor

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
