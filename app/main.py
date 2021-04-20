from fastapi import FastAPI
import uvicorn
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel,HttpUrl
app = FastAPI()

class URL(BaseModel):
    url: HttpUrl

@app.get('/')
def index():
    return {'message': 'Hello World'}

@app.post('/scrap-repos')
async def scrapRepos(url: URL):
    page = await requests.get(str(url.url))
    soup = await BeautifulSoup(page.text, 'html.parser')
    def getTitle():
        return soup.head.find('title').text if soup.head.find('title') else None
    # Getting link to repository file/folder structure
    def getTreeLink():
        # Search the redirect link to the repository's file and folder tree
        return soup.body.find('a',
            attrs={'class': 'd-none js-permalink-shortcut'}).get('href')\
            if soup.body.find('a', attrs={'class': 'd-none js-permalink-shortcut'}).get('href')\
            else None
    # Getting link id for listing all files
    def getIdTree():
        # Search the link Id for listing all files in the desired repository
        href = soup.body.find('a', attrs={'class': 'd-none js-permalink-shortcut'}).get('href')
        result = href.split(sep="/")
        return result[-1]

    # Mining data from files
    async def filesRepository():
        urlFilesRepository = str(url.url) + '/find/' + getIdTree()
        pageList = await requests.get(urlFilesRepository)
        soupList = await BeautifulSoup(pageList.text, 'html.parser')

        string = str(url.url) + '/tree-list/' + getIdTree()
        urlFiles = await requests.get(string)

        return soupList.text if soupList.text else None

    return {
        "title": getTitle(),
        "extension": getTreeLink(),
        "count": filesRepository(),
        "lines": 0,
        "bytes": 0
    }
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4200)