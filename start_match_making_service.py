from app.services.match_making_service import MatchMakingService
from app.extentions.logger import Logger
from config import Config

if __name__ == "__main__":
    Logger.setup_logger(Config.MATCH_MAKING_LOG_FILE)
    _service = MatchMakingService()
    _service.start_service()