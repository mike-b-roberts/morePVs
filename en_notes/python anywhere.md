# python anywhere

 Don't need: git clone <repository URL>

`cd \morePVs `

`python3 morePVs.py`

NB Commented out all `win32` references in `en_utilities` (so `df_to_csv` is now just `df.to_csv`

NB Need to `commit` and `push` all changes to github first, then `pull` (= `fetch` + `merge`)

Issues:

* `win32api` and `pythoncom` removed from `en_utilities`
* Issue in line 44: `self.timeseries.weekday.isin([0, 1, 2, 3, 4])`  whereby: `'numpy.ndarray' object has no attribute 'isin' `. i.e. self.timeseries.weekday is a `np` array. 
  * probably because `pythonanywhere` defaults to `python 2.7`. Bad `pythonanywhere`

So, command is:

`python3 morePVs.py`

 