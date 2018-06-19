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

from mycroft.util.lang.format_common import convert_to_mixed_fraction
from num2words import num2words as n2w
from math import trunc
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

FRACTION_STRING_RU = {
    2: 'вторая',
    3: 'третья',
    4: 'четвертая',
    5: 'пятая',
    6: 'шестая',
    7: 'седьмая',
    8: 'восьмая',
    9: 'девятая',
    10: 'десятая',
    11: 'одиннадцатая',
    12: 'двеннадцатая',
    13: 'тринадцатая',
    14: 'четырнадцатая',
    15: 'пятнадцатая',
    16: 'шестнадцатая',
    17: 'семнадцатая',
    18: 'восемнадцатая',
    19: 'девятнадцатая',
    20: 'двадцатая'
}


def nice_number_ru(number, speech, denominators):
    """ Russian helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 с половиной" for speech and "4 1/2" for text

    Args:
        number (int or float): the float to format
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """
    result = convert_to_mixed_fraction(number, denominators)
    if not result:
        # Give up, just represent as a 3 decimal number
        return str(round(number, 3))

    whole, num, den = result

    if not speech:
        if num == 0:
            # TODO: Number grouping?  E.g. "1,000,000"
            return str(whole)
        else:
            return '{} {}/{}'.format(whole, num, den)

    if num == 0:
        return str(whole)
    den_str = FRACTION_STRING_RU[den]
    if whole == 0:
        if num == 1:
            return_string = 'ноль целых и одна {}'.format(den_str)
        else:
            return_string = 'ноль целых и {} {}'.format(num, den_str)
    elif num == 1:
        return_string = '{} с половиной' if den == 2 else '{} и одна {}'.format(whole, den_str)
    else:
        return_string = '{} и {} {}'.format(whole, num, den_str)
    return return_string


def pronounce_number_ru(num, places=2, agg_minute=False):
    """
    Convert a number to it's spoken equivalent

    For example, '5' would return 'пять',
                 '5.2' would return 'пять целых две десятые',
                 '52.223' would return 'пять две целые двести двадцать три десятых'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
        agg_minute(bool): agree result with minutes noun
    Returns:
        (str): The pronounced number
    """
    result = ""
    if num < 0:
        result = "минус "

    num = abs(num)
    whole = trunc(num)
    nice = nice_number_ru(num, True, list(range(2, 19)))

    try:
        float(nice)  # Will throw ValueError if %num% can be "nice-numbered"
        result += n2w(num, lang='ru')
    except ValueError:
        result += n2w(whole, lang='ru')
        result += nice[nice.find(' '):]

    if agg_minute and 0 < int(str(whole)[-1]) < 3 and not (10 < whole < 20):
        result = result.split()
        result[-1] = morph.parse(result[-1])[0].inflect({"femn"}).word
        result = ' '.join(result)

    return result


def hour_text_num_agree(hour):
    return morph.parse('час')[0].make_agree_with_number(hour).word


def min_text_num_agree(minute):
    return morph.parse('минута')[0].make_agree_with_number(minute).word


def nice_time_ru(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'пять часов тридцать минут' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""
        speak += '{} {} {} {}'.format(pronounce_number_ru(dt.hour),
                                      hour_text_num_agree(dt.hour),
                                      pronounce_number_ru(dt.minute, agg_minute=True),
                                      min_text_num_agree(dt.minute))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "полночь"
        if dt.hour == 12 and dt.minute == 0:
            return "полдень"

        res_hour = dt.hour - 12
        if dt.hour == 0:
            res_hour = 12
        elif dt.hour < 13:
            res_hour = dt.hour

        speak = pronounce_number_ru(res_hour) + " " + hour_text_num_agree(res_hour)

        if dt.minute == 0:
            if not use_ampm:
                return speak
        else:
            speak += " и " + pronounce_number_ru(dt.minute, agg_minute=True) + " " + min_text_num_agree(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " после полудня"
            else:
                speak += " до полудня"

        return speak
