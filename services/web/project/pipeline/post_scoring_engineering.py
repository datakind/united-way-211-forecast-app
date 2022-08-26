from .abstract.pipeline_abc import post_scoring_engineering


class PostScoringEngineering(post_scoring_engineering):
    def read_input(self):
        pass

    def post_scoring_engineering(self):
        pass

    def write_output(self):
        pass
