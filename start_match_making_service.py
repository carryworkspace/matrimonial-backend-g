from app.services.match_making_service import MatchMakingService

if __name__ == "__main__":
    _service = MatchMakingService()
    _service.start_service()