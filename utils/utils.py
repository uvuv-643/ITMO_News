# to get from yagpt response actual number of answer

from typing import List
import numpy as np
import re


def split_on_words(text):
    cleaned_text = re.sub(r'[^\w\s]', ' ', text)
    words = cleaned_text.split()
    return words


def levenshtein(a,b,ratio=False,print_matrix=False,lowercase=True) :
	if type(a) != type('') :
		raise TypeError('First argument is not a string!')
	if type(b) != type('') :
		raise TypeError('Second argument is not a string!')
	if a == '' :
		return len(b)
	if b == '' :
		return len(a)
	if lowercase :
		a = a.lower()
		b = b.lower()

	n = len(a)
	m = len(b)
	lev = np.zeros((n+1,m+1))

	for i in range(0,n+1) :
		lev[i,0] = i 
	for i in range(0,m+1) :
		lev[0,i] = i

	for i in range(1,n+1) :
		for j in range(1,m+1) :
			insertion = lev[i-1,j] + 1
			deletion = lev[i,j-1] + 1
			substitution = lev[i-1,j-1] + (1 if a[i-1]!= b[j-1] else 0)
			lev[i,j] = min(insertion,deletion,substitution)

	if print_matrix :
		print(lev)

	if ratio :
		return (n+m-lev[n,m])/(n+m)
	else :
		return lev[n,m]