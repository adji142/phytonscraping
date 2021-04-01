# import demoji

emojilist = "SERIUS.. ADA APA LOE SAMA BETRAND PETO⁉️ RUBEN ONSU. IVAN GUNAWAN - Deddy Corbuzier Podcast"

# demoji.findall(emojilist)
o="Team yg nonton doang ketawa2 sampe sedih2 tapi gak vote awra qarisma🙋🙋🙋asdasdasd addasd"

import re

my_str = "hey th~!ere"
my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', o)
print(my_new_string)