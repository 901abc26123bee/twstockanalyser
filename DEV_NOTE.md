## setup Virtual Env for python
python3 --version 
### virtualenv(.venv)

使用 Python 做開發的人，多數都會使用虛擬環境，特別是 virtualenv 作為建立開發並隔離環境的方式，而且這個工作的流程不外乎就是：
  透過建立虛擬環境 virtualenv 來隔離 Python 的開發環境
  進入虛擬環境後，透過 pip 下載套件
  為了方便後續專案的保存、上版控與移轉，透過建立 requirements.txt 來保存虛擬環境中透過 pip 所安裝的套件
  但是現有透過建立虛擬環境隔離與產生 requirements.txt 保存該虛擬環境中所安裝的套件都會有一些問題：
  - requirements.txt 是需要手動更新的，所以當透過 pip 下載或更新套件後，requirements.txt 是不會自動更新。因此專案移轉時，若忘記更新 requirements.txt 會導致新安裝的套件或是更新的套件都沒有被記錄下來，拿到你專案的人也會無法跑起來。
因此雖然 virtualenv 是一個可以幫助我們在開發 Python 專案時，隔離主系統與其他專案環境的好工具，但是 virtualenv 依然不夠好用。
所以 Pipenv 便隨之誕生了，一套更強的虛擬環境與套件管理的工具利器。

https://pythonviz.com/basic/visual-studio-code-virtual-environment-setup/

https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe

https://www.eachtechabc.com/2020/07/pipenv-virtualenv.html

1. ctrl+shift+p  -> Python: Select Interpreter  -> Create Virtual Environment --> select python version

2, after that , you will see `.venv` folder in your project
```sh
virtualenv .venv  
python3 -version  
Python 3.11.6 // should be same as your python version in .venv folder
```


remove
```sh
rm -rf .venv
```

### pipenv
https://note.koko.guru/posts/python-pipenv-install-and-usage
https://stackoverflow.com/questions/46391721/pipenv-command-not-found


1. 建立虛擬環境
進入要開發並準備建立虛擬環境的專案，透過 pipenv install 來建立虛擬環境，此時 pipenv install 會偵測你系統預設的 Python 版本環境，並且依照此版本建立虛擬環境：
```sh
sudo pip3 install pipenv # install globally (system wide)

pipenv --python 3.11 # sets up the virtual environment with the specified Python version.
pipenv install # install dependencies listed in the Pipfile of your project. If the Pipfile is absent, it will create a new one and then install any dependencies listed in it

# pipenv install manages and installs project dependencies.
# pipenv --python 3.11 specifies the Python version for the virtual environment.
```

2. 啟動虛擬環境
當建立好虛擬環境以及 Pipfile, Pipfile.lock 後，接著就是要進入虛擬環境中來在環境之下操作，在 Pipenv 中提供了 pipenv shell 這個指令能使用我進入環境中：
```sh 
# 啟動虛擬環境
$ pipenv shell
Launching subshell in virtual environment...
 . /Users/tina_wong/.local/share/virtualenvs/py-stock-Hrm0psK8/bin/activate

# 查詢虛擬環境所在位置
$ pipenv --venv
/Users/tina_wong/.local/share/virtualenvs/py-stock-Hrm0psK8
```

3. 退出虛擬環境
如果你在虛擬環境中，想要退出的話，可以輸入 deactivate 或是按下 Ctrl + D 即可。

```sh
pipenv --rm
```

4. 安裝套件在虛擬環境中
```sh
$ pipenv install requests
$ pipenv install beautifulsoup4
$ pipenv install yfinance pandas
```

[pipenv-stuck-locking](https://stackoverflow.com/questions/56440090/pipenv-stuck-locking)
[Pipenv lock hangs #2681](https://github.com/pypa/pipenv/issues/2681)

### Vscode
problem: Go to definition not working
solution:
    https://stackoverflow.com/questions/64255834/no-definition-found-for-function-vscode-python
    https://stackoverflow.com/questions/68637153/python-error-in-vscode-sorry-something-went-wrong-activating-intellicode-suppo


problem: vscode integrated terminal is black screen and unable to stdin (for python project only)
    https://stackoverflow.com/questions/74156960/vs-code-terminal-not-running-at-all
solution:
    https://stackoverflow.com/questions/54582361/vscode-terminal-shows-incorrect-python-version-and-path-launching-terminal-from
    ```json
    "terminal.integrated.inheritEnv": false,
    ```

vscode debug test for python:
    https://stackoverflow.com/questions/52462599/visual-studio-code-with-python-timeout-waiting-for-debugger-connection

### python module
[ModuleNotFoundError：如何解决 no module named Python 错误？](https://www.freecodecamp.org/chinese/news/module-not-found-error-in-python-solved/)
[Execution of Python code with -m option or not [duplicate]](https://stackoverflow.com/questions/22241420/execution-of-python-code-with-m-option-or-not)
[What is __main__.py?](https://stackoverflow.com/questions/4042905/what-is-main-py)

```py
if __name__=='__main__':
    test()
```
當我們在命令列運行模組檔案時，Python解釋器把一個特殊變數__name__置為__main__，而如果在其他地方導入該該模組時，if判斷將失敗，因此，這種if測試可以讓一個模組透過命令列運行時執行一些額外的程式碼，最常見的就是執行測試。

```sh
# after download twstockanalyzer
cd twstockanalyzer/
python -m twstockanalyzer -H
```


### stock url
下載台股代碼清單
首先，先透過證交所的個股日成交資訊API下載最新的收盤資料,，目的是為了取得股票代碼清單。當然，你可以直接下載Excel或CSV檔，也可以透過以下的程式下載。
import requests
import numpy as np
import pandas as pd

link = 'https://quality.data.gov.tw/dq_download_json.php?nid=11549&md5_url=bb878d47ffbe7b83bfc1b41d0b24946e'
r = requests.get(link)
data = pd.DataFrame(r.json())

data.to_csv(儲存路徑 + '/stock_id.csv', index=False, header = True)
下載Yahoo股市資料
根據〈Free Stock Data for Python Using Yahoo Finance API〉.)的說法，Yahoo Finance的API的限制為：Using the Public API (without authentication), you are limited to 2,000 requests per hour per IP (or up to a total of 48,000 requests a day)。在我用以下的code抓取1116支股票的歷史記錄後，確實沒有被阻擋的問題。


### python
`__init__.py`
https://stackoverflow.com/questions/37139786/is-init-py-not-required-for-packages-in-python-3-3



When you run twstock directly as a script, Python may treat the module path differently. If you run:

```sh
python -m twstock
```
Python executes `twstock/__main__.py` as the entry point, and the twstock package should be properly imported. However, the context of the `__main__.py` execution is crucial.

```sh
python -m twstockanalyzer -A
python -m twstockanalyzer -U
```

### func 定義預設參數
定義預設參數要牢記一點：預設參數必須指向不變物件！

要修改上面的例子，我們可以用None這個不變物件來實現：

```py
def add_end(L=None):
    if L is None:
        L = []
    L.append('END')
    return L
現在，無論呼叫多少次，都不會有問題：

>>> add_end()
['END']
>>> add_end()
['END']
```
為什麼要設計str、None這樣的不變物件呢？因為不變物件一旦創建，物件內部的資料就不能修改，這樣就減少了因為修改資料而導致的錯誤。此外，由於物件不變，多任務環境下同時讀取物件不需要加鎖，同時讀一點問題都沒有。我們在寫程式時，如果可以設計一個不變對象，那就盡量設計成不變對象。




## Stock holder Info
https://www.twse.com.tw/rwd/zh/fund/T86?date=20240916&selectType=ALL&response=csv


## Formatter for py
```sh
pip install black
black .

pip install yapf
yapf -i -r .
```

## docker 
docker compose up --build


Summary
- Use pandas.DataFrame when you need to handle complex data analysis, work with large datasets, or perform operations on entire columns.
- Use namedtuple when you need a lightweight, immutable way to group related data together without the overhead of a full DataFrame.

If you're working with structured data that requires frequent manipulation, go with DataFrame. For simpler, more static data structures, namedtuple is a great choice!


## Git
```sh
git fetch origin: This retrieves the latest changes from the remote repository but does not merge them into your local branches.

git checkout master: This switches to your local master branch.

git reset --hard origin/master: This forcefully resets your local master branch to match the state of origin/master. Any local commits or changes in the master branch will be lost.
```


python -m twstockanalyzer -A d
python -m twstockanalyzer -A tm
python -m twstockanalyzer -A tp