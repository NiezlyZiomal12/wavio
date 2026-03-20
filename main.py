from src.scenes import StateManager


def run_game() -> None:
    state_manager = StateManager()
    state_manager.run()


if __name__ == "__main__":
    run_game()
