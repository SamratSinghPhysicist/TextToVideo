from duckduckgo_search import DDGS




def generateDDG_ai_chat(promt, model_to_use):
    
    """
    # AI Chat:
    Models Supported = ["gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
            "o3-mini", "mixtral-8x7b"]
    """
    results = DDGS().chat(promt, model=model_to_use)

    print(results)
    return results

"""
NOTE: Image Generating fucntion was NOT Working
"""
def video_search_DDG(query, num_of_results):
    
    results = DDGS().videos(
        keywords=query,
        region="wt-wt",
        safesearch="off",
        timelimit="w",
        resolution="high",
        duration="medium",
        max_results=num_of_results,
    )
    print(results)
    return results

def news_search_DDG(query, num_of_results):
    
    results = DDGS().news(
        keywords=query,
        region="wt-wt",
        safesearch="off",
        timelimit="w",
        resolution="high",
        duration="medium",
        max_results=num_of_results,
    )
    print(results)
    return results

