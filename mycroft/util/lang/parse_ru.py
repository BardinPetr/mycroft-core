# -*- coding: utf-8 -*-
#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mycroft.util.lang.parse_common import is_numeric, look_for_fractions
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()


def isFractional_ru(input_str):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    pre = input_str.lower().split()

    if len(pre) == 1:
        input_str = morph.parse(input_str)[0].normal_form
        if input_str == "целое":
            return 1.0
        if input_str == "половина":
            return 1.0 / 2
        if input_str == "полтора":
            return 3.0 / 2
        if input_str == "треть":
            return 1.0 / 3
        if input_str == "четверть":
            return 1.0 / 4
    elif len(pre) == 2:
        aFrac = ["один", "два", "три", "четыре", "пять", "шесть",
                 "семь", "восемь", "девять", "десять", "одиннадцать", "двенадцать"]
        bFrac = {"треть": 3, "четверть": 4}

        first, second = map(lambda x: morph.parse(x)[0].normal_form, pre)

        if first in aFrac and second in aFrac:
            return (aFrac.index(first) + 1) / (aFrac.index(second) + 1)
        elif first in aFrac and second in bFrac:
            return (aFrac.index(first) + 1) / bFrac[second]
    return False


def normalize_ru(text, remove_articles=True):
    """ Russian string normalization """

    articles = ["и", "с", "а", "еще"]

    words = text.replace('ё', 'е').split()  # this also removed extra spaces
    normalized = ""
    f = False

    for count in range(len(words)):
        if f:
            f = False
            continue

        word = words[count]
        if word in articles:
            continue

        text_numbers = ["ноль", "один", "два", "три", "четыре", "пять", "шесть",
                        "семь", "восемь", "девять", "десять", "одиннадцать", "двенадцать",
                        "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать",
                        "семнадцать", "восемнадцать", "девятнадцать", "двадцать"]
        nf_word = morph.parse(word)[0].normal_form

        if isFractional_ru(nf_word):
            word = str(round(isFractional_ru(nf_word), 4))
        else:
            if (count + 1) < len(words):
                pre = isFractional_ru(nf_word + " " + morph.parse(words[count + 1])[0].normal_form)
                word = str(round(pre, 4)) if pre else word
                f = pre
        if not f:
            word = str(text_numbers.index(nf_word)) if nf_word in text_numbers else word

        normalized += " " + word

    return normalized[1:]  # strip the initial space


def extractnumber_ru(text):
    """
    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.
    Args:
        text (str): the string to normalize
    Returns:
        (int) or (float): The value of extracted number

    """

    # Convert fractions like "2/3" to "0.6667"
    text = normalize_ru(text)
    fracs = re.findall('\d+\s*/\s*\d+', text)
    for f in fracs:
        res = re.findall('\d+', f)
        text = text.replace(f, str(round(float(res[0]) / float(res[1]), 4)))

    # Get numbers from string & sum
    a_words = text.split()
    val = False
    for count in range(len(a_words)):
        word = a_words[count]
        if is_numeric(word):
            nw = float(word)
            val = (val + nw) if val else nw
        elif val:
            break
    return val


def extract_datetime_ru(string, currentDate=None):
    # TODO finish this function
    return [datetime.now(), string]
