import requests
import json
import re
import random
import signal
import sys
import time
import cv2
import numpy as np

accesstoken = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
instance = "kirishima.cloud"
othello_black = ":o_bl:"
othello_white = ":o_wh:"
othello_board = ":o_bo:"
BOARD = 2
BLACK = 1
WHITE = 0
bot_account = ""
toot_account = ""

def picture_to_dot(tootjson, is_emphasis):
    for i in range(MAX_RETRIES):
        try:
            r = requests.get(tootjson["media_attachments"][0]["url"], stream=True, timeout=(3.0, 27))
            #if r.status_code == 200:
            break
            #else:
            #    continue
        except requests.exceptions.ReadTimeout as err:
            print(err, file=sys.stderr)
            time.sleep(10)
        except requests.exceptions.RequestException as err:
            print(err, file=sys.stderr)
            time.sleep(10)
        except requests.Timeout as err:
            print(err, file=sys.stderr)
            time.sleep(10)
        except KeyboardInterrupt as err:
            print(err, file=stderr)
            print("終了します")
            exit()
        except Exception as err:
            print(err, file=sys.stderr)
            time.sleep(10)
    else:
        print("all tries failed when download picture", file=sys.stderr)
        return

    with open("tmp.png", 'wb') as f:
        f.write(r.content)

    img = cv2.imread("tmp.png", cv2.IMREAD_COLOR)

#    for y in range(img.shape[0]):
#            for x in range(img.shape[1]):
#                if img[y, x, 3] == 0:
#                    img[y, x] = [255, 255, 255, 255]

    tmp = img[:, :]
    height, width = img.shape[:2]
    if(height > width):
        size = height
        limit = width
    else:
        size = width
        limit = height
    start = int((size - limit) / 2)
    fin = int((size + limit) / 2)
    new_img = cv2.resize(np.zeros((1, 1, 3), np.uint8), (size, size))
    if(size == height):
        new_img[:, start:fin] = tmp
    else:
        new_img[start:fin, :] = tmp

    #clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
    #processed_img = clahe.apply(new_img)

    #scaled = cv2.resize(new_img, dsize=(14, 11), interpolation=cv2.INTER_NEAREST)
    if(is_emphasis):
        scaled = cv2.resize(new_img, dsize=(14, 11), interpolation=cv2.INTER_CUBIC)
    else:
        scaled = cv2.resize(new_img, dsize=(14, 11), interpolation=cv2.INTER_AREA)
    #scaled = cv2.resize(new_img, dsize=(14, 11), interpolation=cv2.INTER_LANCZOS4)

#    width = tootjson["media_attachments"][0]["meta"]["original"]["width"]
#    height = tootjson["media_attachments"][0]["meta"]["original"]["height"]

    color = [[[0 for i in range(3)] for j in range(14)] for k in range(11)]

    for y in range(0, 11):
        for x in range(0, 14):
#            imgbox = processed_img[int(y * (size / 11)): int(y * (size / 11) + (size / 11)), int(x * (size / 14)): int(x * (size + 14) + (size + 14))]
#            imgbox = scaled[y:y + 1, x:x + 1]
#            color[y][x][0] = int(imgbox.T[2].flatten().mean()) #R
#            color[y][x][1] = int(imgbox.T[1].flatten().mean()) #G
#            color[y][x][2] = int(imgbox.T[0].flatten().mean()) #B
            color[y][x][0] = scaled.item(y, x, 2)
            color[y][x][1] = scaled.item(y, x, 1)
            color[y][x][2] = scaled.item(y, x, 0)

    toottext = ""

    for y in range(0, 11):
        for x in range(0, 14):
            toottext = toottext + "[colorhex={:02x}{:02x}{:02x}]█[/colorhex]".format(color[y][x][0], color[y][x][1], color[y][x][2])
        toottext = toottext + "\n"

    post_toot(toottext)

def othello_ai(int_board, stone_color_of_computer):
    can_get_stone = {}
    for x in range(8):
        for y in range(8):
            #print(x,y)
            can_get_stone.update({(x * 8 + y):try_get_stone(int_board, x, y, stone_color_of_computer)})
    place_of_put_stone = max(can_get_stone, key=(lambda x: can_get_stone[x]))
    #print(place_of_put_stone)
    #exit()
    #place_of_put_stone = random.choice(place_of_put_stone)
    x = int((place_of_put_stone - place_of_put_stone % 8) / 8)
    y = place_of_put_stone % 8
    int_board[x][y] = stone_color_of_computer

    i = 1
    while(1):
        if (x + i) < 8 and int_board[x + i][y] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x + i) == 8 or int_board[x + i][y] == BOARD:
                i = 0
                break
            if int_board[x + i][y] == stone_color_of_computer:
                i -= 1
                break

    if i > 0:
        for stone in range(1, i + 1):
            int_board[x + stone][y] = stone_color_of_computer

    i = 1
    while(1):
        if (x + i) < 8 and (y + i) < 8 and int_board[x + i][y + i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x + i) == 8 or (y + i) == 8 or int_board[x + i][y + i] == BOARD:
                i = 0
                break
            if int_board[x + i][y + i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x + stone][y + stone] = stone_color_of_computer

   
    i = 1
    while(1):
        if (y + i) < 8 and int_board[x][y + i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (y + i) == 8 or int_board[x][y + i] == BOARD:
                i = 0
                break
            if int_board[x][y + i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x][y + stone] = stone_color_of_computer

    i = 1
    while(1):
        if (x - i) >= 0 and (y + i) < 8 and int_board[x - i][y + i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x - i) < 0 or (y + i) == 8 or int_board[x - i][y + i] == BOARD:
                i = 0
                break
            if int_board[x - i][y + i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x - stone][y + stone] = stone_color_of_computer

    i = 1
    while(1):
        if (x - i) >= 0 and int_board[x - i][y] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x - i) < 0 or int_board[x - i][y] == BOARD:
                i = 0
                break
            if int_board[x - i][y] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x - stone][y] = stone_color_of_computer

    i = 1
    while(1):
        if (x - i) >= 0 and (y - i) >= 0 and int_board[x - i][y - i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x - i) < 0 or (y - i) < 0 or int_board[x - i][y - i] == BOARD:
                i = 0
                break
            if int_board[x - i][y - i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x - stone][y - stone] = stone_color_of_computer

    i = 1
    while(1):
        if (y - i) >= 0 and int_board[x][y - i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (y - i) < 0 or int_board[x][y - i] == BOARD:
                i = 0
                break
            if int_board[x][y - i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x][y - stone] = stone_color_of_computer

    i = 1
    while(1):
        if (x + i) < 8 and (y - i) >= 0 and int_board[x + i][y - i] == int(not stone_color_of_computer == True):
            i += 1
        else:
            if (x + i) == 8 or (y - i) < 0 or int_board[x + i][y - i] == BOARD:
                i = 0
                break
            if int_board[x + i][y - i] == stone_color_of_computer:
                i -= 1
                break
    if i > 0:
       for stone in range(1, i + 1):
           int_board[x + stone][y - stone] = stone_color_of_computer

    return int_board

def try_get_stone(int_board, x, y, stone_color_of_computer):
    if int_board[x][y] != BOARD:
        return 0
    if int_board[x][y] == BOARD:

        i = 1
        while(1):
            if (x + i) < 8 and int_board[x + i][y] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x + i) == 8 or int_board[x + i][y] == BOARD:
                    i = 0
                    break
                if int_board[x + i][y] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone = i
        
        i = 1
        while(1):
            if (x + i) < 8 and (y + i) < 8 and int_board[x + i][y + i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x + i) == 8 or (y + i) == 8 or int_board[x + i][y + i] == BOARD:
                    i = 0
                    break
                if int_board[x + i][y + i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i
        
        i = 1
        while(1):
            if (y + i) < 8 and int_board[x][y + i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (y + i) == 8 or int_board[x][y + i] == BOARD:
                    i = 0
                    break
                if int_board[x][y + i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        i = 1
        while(1):
            if (x - i) >= 0 and (y + i) < 8 and int_board[x - i][y + i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x - i) < 0 or (y + i) == 8 or int_board[x - i][y + i] == BOARD:
                    i = 0
                    break
                if int_board[x - i][y + i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        i = 1
        while(1):
            if (x - i) >= 0 and int_board[x - i][y] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x - i) < 0 or int_board[x - i][y] == BOARD:
                    i = 0
                    break
                if int_board[x - i][y] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        i = 1
        while(1):
            if (x - i) >= 0 and (y - i) >= 0 and int_board[x - i][y - i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x - i) < 0 or (y - i) < 0 or int_board[x - i][y - i] == BOARD:
                    i = 0
                    break
                if int_board[x - i][y - i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        i = 1
        while(1):
            if (y - i) >= 0 and int_board[x][y - i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (y - i) < 0 or int_board[x][y - i] == BOARD:
                    i = 0
                    break
                if int_board[x][y - i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        i = 1
        while(1):
            if (x + i) < 8 and (y - i) >= 0 and int_board[x + i][y - i] == int(not stone_color_of_computer == True):
                i += 1
            else:
                if (x + i) == 8 or (y - i) < 0 or int_board[x + i][y - i] == BOARD:
                    i = 0
                    break
                if int_board[x + i][y - i] == stone_color_of_computer:
                    i -= 1
                    break
        can_get_stone += i

        return can_get_stone

def make_othello_int_board(char_board):
    int_board = [[0 for i in range(8)] for j in range(8)]
    #char_board = re.split("[ \n]", char_board)
    char_board = re.sub("[\u200b\s\n]", "", char_board)
    char_board = char_board.replace("::", ": :")
    char_board = char_board.split()
    #print(char_board)

    for x in range(8):
        for y in range(8):
            if char_board[x * 8 + y] == othello_black:
                int_board[x][y] = BLACK
            if char_board[x * 8 + y] == othello_white:
                int_board[x][y] = WHITE
            if char_board[x * 8 + y] == othello_board:
                int_board[x][y] = BOARD
    return int_board

def customemoji_othello(toot_content):
    toot_content = toot_content.strip("<p>").strip("</p>")
    toot_content = toot_content.replace("<br />", "\n")
    #print(toot_content)
    board_re = re.search("((?:(?:\s|\u200b)*(?:(?:%s|%s|%s)(?:\s|\u200b)+){7}(?:%s|%s|%s)(?:\n|)){8})" %(othello_black, othello_white, othello_board, othello_black, othello_white, othello_board), toot_content)
    #print(board_re.group())
    #board_re = re.search("(((%s|%s|%s)(\s|)*){8}(\n|)){8}" %(othello_black, othello_white, othello_board), toot_content)
    #board = re.sub(".*(?=((%s|%s|%s)(\s|)){8})", "test", toot_content)
    if board_re:
        #print("find othello board")
        #print(board_re.group(1))
        othello_int_board = make_othello_int_board(board_re.group(1))
        othello_int_board = othello_ai(othello_int_board, WHITE) #computer's stone color is white.
        post_othello_toot(othello_int_board)

def post_othello_toot(int_board):
    content = ""
    for x in range(8):
        for y in range(8):
            if int_board[x][y] == BLACK:
                content = content + othello_black
            elif int_board[x][y] == WHITE:
                content = content + othello_white
            elif int_board[x][y] == BOARD:
                content = content + othello_board
            if y != 7:
                content = content + " "
        content = content + "\n"
    post_toot(content)

def judge_janken(computer, player):
    if computer == player:
        return "あいこ"
    elif (computer == 0 and player == 2) or (computer == 1 and player == 0) or (computer == 2 and player == 1):
        return "プレイヤーの勝ち"
    else:
        return "コンピューターの勝ち"

def num_to_hand(num):
    if num == 0:
        return "グー"
    if num == 1:
        return "チョキ"
    if num == 2:
        return "パー"

def janken_toot(player):
    computer = random.randint(0, 2)
    judge = judge_janken(computer, player)
    hand_computer = num_to_hand(computer)
    post_toot("コンピューターは" + hand_computer + "\n" + judge)

def janken():
    gu = re.search("(じゃんけん|ジャンケン).*(グー|ぐー)", tootjson["content"])
    tyoki = re.search("(じゃんけん|ジャンケン).*(チョキ|ちょき)", tootjson["content"])
    pa = re.search("(じゃんけん|ジャンケン).*(パー|ぱー)", tootjson["content"])
    if gu and not tyoki and not pa:
        janken_toot(0)
    if not gu and tyoki and not pa:
        janken_toot(1)
    if not gu and not tyoki and pa:
        janken_toot(2)

MAX_RETRIES = 2

def post_toot(content):
    #TODO トゥート回数制限
    for i in range(MAX_RETRIES):
        try:
             r = requests.post("https://" + instance + "/api/v1/statuses", params = {"status":content, "visibility":"public"}, headers={"Authorization":"Bearer " + accesstoken}, stream=True, timeout=(3.0, 27))
            #if r.status_code == 200:
            #    break
             break
        except requests.exceptions.ReadTimeout as err:
            print(err, file=sys.stderr)
        except requests.Timeout as err:
            print(err, file=sys.stderr)
        except KeyboardInterrupt as err:
            print(err, file=stderr)
            print("終了します")
            exit()
        except requests.exceptions.RequestException as err:
             print(err, file=sys.stderr)
        except Exception as err:
             print(err, file=sys.stderr)
    else:
        print("all tries failed when post_toot", file=sys.stderr)

def terminateProcess(signalNumber, frame):
    post_toot("終了します")
    sys.exit()

if __name__ == "__main__":

    signal.signal(signal.SIGTERM, terminateProcess)
    signal.signal(signal.SIGINT, terminateProcess)

    post_toot("起動しました")

    while True:
        try:
            r = requests.get("https://" + instance + "/api/v1/streaming/public/local", headers={"Authorization":"Bearer " + accesstoken}, stream=True, timeout=(3.0, 27))
            #if r.status_code == 200:
            break
            #else:
            #    continue
        except requests.exceptions.ReadTimeout as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except requests.Timeout as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except KeyboardInterrupt as err:
            print(err, file=stderr)
            print("終了します")
            exit()
        except requests.exceptions.RequestException as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except Exception as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)

    while True:
        try:
            user = requests.get("https://" + instance +"/api/v1/accounts/verify_credentials", headers={"Authorization":"Bearer " + accesstoken}, timeout=(3.0, 27)).json()
            #if user.status_code == 200:
            break
            #else:
            #    continue
        except requests.exceptions.ReadTimeout as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except requests.exceptions.RequestException as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except requests.Timeout as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)
        except KeyboardInterrupt as err:
            print(err, file=stderr)
            print("終了します")
            exit()
        except Exception as err:
            print(err, file=sys.stderr)
            time.sleep(60 * 5)

    bot_account = user["acct"]

    is_update = 0
    for line in r.iter_lines():
        data = line.decode("utf-8")
        if data.find("update") != -1:
            is_update = 1
            continue
        is_data = data.find("data")
        if (is_data != -1) and (is_update == 1):
            is_update = 0
            toot = data.split(":", 1)
            toottext = toot[1].strip()
            try:
                tootjson = json.loads(toottext)
            except Exception as err:
                print(err, file=sys.stderr)
                continue
            toot_account = tootjson["account"]["acct"]
            if toot_account == bot_account:
                continue
            #print(tootjson["content"])
            #print(tootjson)
            #print(user.keys())
            if tootjson["content"].find("にゃーん") != -1:
                post_toot("にゃーん")
            janken();
            customemoji_othello(tootjson["content"]);
            if tootjson["content"].find("強調したドット絵にして") != -1 and len(tootjson["media_attachments"]) > 0:
                picture_to_dot(tootjson, 1)
            elif tootjson["content"].find("ドット絵にして") != -1 and len(tootjson["media_attachments"]) > 0:
                picture_to_dot(tootjson, 0)
