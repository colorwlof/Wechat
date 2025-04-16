# 创建应用实例
import sys

from wxcloudrun import app
import random
import re
import time
import itertools
from itertools import starmap
from bidict import bidict
from datetime import datetime, timedelta
import config

def test_qimen(start_datetime, end_datetime):
    # Ensure end_datetime is greater than start_datetime
    if end_datetime <= start_datetime:
        raise ValueError("End datetime must be greater than start datetime")
    # Initialize current_datetime to start_datetime
    current_datetime = start_datetime
    # Loop through each hour from start_datetime to end_datetime
    while current_datetime <= end_datetime:
        year = current_datetime.year
        month = current_datetime.month
        day = current_datetime.day
        hour = current_datetime.hour
        minute = current_datetime.minute  # Keep it 0 for each hour
        try:
            p = Qimen(year, month, day, hour, minute).pan(2)
            print(f"Successfully executed for {current_datetime}")
        except Exception as e:
            print(f"Error at {current_datetime}: {e}")
        # Move to the next hourpip
        current_datetime += timedelta(hours=1)


class Qimen:
    """奇門函數"""

    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    def year_yuen(self):
        """搵上中下元"""
        yuen_list = [(i * 60) + 4 for i in range(22, 100)]
        three_yuen = itertools.cycle([i + "元甲子" for i in list("上中下")])
        for yuen in yuen_list:
            if self.year < yuen:
                break
            yuen1 = dict(zip(yuen_list, three_yuen)).get(yuen_list[yuen_list.index(yuen) - 1])
            return [yuen1, yuen_list[yuen_list.index(yuen) - 1]]
        return None

    def qimen_ju_day(self):
        """奇門局日"""
        ju_day_dict = {tuple(list("甲己")): "甲己日",
                       tuple(list("乙庚")): "乙庚日",
                       tuple(list("丙辛")): "丙辛日",
                       tuple(list("丁壬")): "丁壬日",
                       tuple(list("戊癸")): "戊癸日"}
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        try:
            find_d = config.multi_key_dict_get(ju_day_dict, gz[2][0])
        except TypeError:
            find_d = config.multi_key_dict_get(ju_day_dict, gz[2][1])
        return find_d

    # 值符
    def hourganghzi_zhifu(self):
        """時干支值符"""
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        jz = config.jiazi()
        a = list(map(lambda x: config.new_list(jz, x)[0:10], jz[0::10]))
        b = list(map(lambda x: jz[0::10][x] + config.tian_gan[4:10][x], list(range(0, 6))))
        d = dict(zip(list(map(lambda x: tuple(x), a)), b))
        return config.multi_key_dict_get(d, gz[3])

    # 分值符
    def hourganghzi_zhifu_minute(self):
        """刻家奇門值符"""
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        jz = config.jiazi()
        a = list(map(lambda x: tuple(x), list(map(lambda x: config.new_list(jz, x)[0:10], jz[0::10]))))
        b = list(map(lambda x: jz[0::10][x] + config.tian_gan[4:10][x], list(range(0, 6))))
        return config.multi_key_dict_get(dict(zip(a, b)), gz[4])

    # 地盤
    def pan_earth(self, option):
        """時家奇門地盤設置, option 1:拆補 2:置閏"""
        chaibu = config.qimen_ju_name_chaibu(self.year,
                                             self.month,
                                             self.day,
                                             self.hour,
                                             self.minute)
        zhirun = config.qimen_ju_name_zhirun(self.year,
                                             self.month,
                                             self.day,
                                             self.hour,
                                             self.minute)
        qmju = {1: chaibu, 2: zhirun}.get(option)
        return dict(zip(list(map(lambda x: dict(zip(config.cnumber, config.eight_gua)).get(x),
                                 config.new_list(config.cnumber, qmju[2]))),
                        {"陽遁": list("戊己庚辛壬癸丁丙乙"),
                         "陰遁": list("戊乙丙丁癸壬辛庚己")}.get(qmju[0:2])))

    # 地盤
    def pan_earth_minute(self):
        """刻家奇門地盤設置"""
        ke = config.qimen_ju_name_ke(self.year,
                                     self.month,
                                     self.day,
                                     self.hour,
                                     self.minute)
        return dict(zip(list(map(lambda x: dict(zip(config.cnumber, config.eight_gua)).get(x),
                                 config.new_list(config.cnumber, ke[2]))),
                        {"陽遁": list("戊己庚辛壬癸丁丙乙"),
                         "陰遁": list("戊乙丙丁癸壬辛庚己")}.get(ke[0:2])))

    # 逆地盤
    def pan_earth_r(self, option):
        """時家奇門地盤(逆)設置, option 1:拆補 2:置閏"""
        pan_earth_v = list(self.pan_earth(option).values())
        pan_earth_k = list(self.pan_earth(option).keys())
        return dict(zip(pan_earth_v, pan_earth_k))

    def pan_earth_min_r(self):
        """刻家奇門地盤(逆)設置"""
        pan_earth_v = list(self.pan_earth_minute().values())
        pan_earth_k = list(self.pan_earth_minute().keys())
        return dict(zip(pan_earth_v, pan_earth_k))

    # 天盤
    def pan_sky(self, option):
        qmju = {
            1: config.qimen_ju_name_chaibu,
            2: config.qimen_ju_name_zhirun
        }.get(option)(self.year,
                      self.month,
                      self.day,
                      self.hour,
                      self.minute)
        rotate = {
            "陽": config.clockwise_eightgua,
            "陰": list(reversed(config.clockwise_eightgua))
        }.get(qmju[0])
        zhifu_n_zhishi = config.zhifu_n_zhishi(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            option)
        fu_head = self.hourganghzi_zhifu()[2]
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        fu_location = self.pan_earth_r(option).get(gz[3][0])
        fu_head_location = zhifu_n_zhishi.get("值符星宮")[1]
        fu_head_location2 = self.pan_earth_r(option).get(fu_head)
        gan_head = zhifu_n_zhishi.get("值符天干")[1]
        zhifu = zhifu_n_zhishi["值符星宮"][0]
        earth = self.pan_earth(option)
        gong_reorder = config.new_list(rotate, "坤")
        if fu_head_location == "中":
            try:
                a = list(map(earth.get, rotate))
                gan_reorder = config.new_list(a, fu_head)
                gong_reorder = config.new_list(rotate, fu_head_location)
                return dict(zip(gong_reorder, gan_reorder))
            except ValueError:
                if config.pan_god(self.year,
                                  self.month,
                                  self.day,
                                  self.hour,
                                  self.minute,
                                  option).get("坤") != "符":
                    a = list(map(earth.get, rotate))
                    return dict(zip(gong_reorder, config.new_list(a, self.pan_earth(option).get("坤"))))
                if earth.get("坤") == gan_head:
                    a = list(map(earth.get, rotate))
                    return dict(zip(gong_reorder, config.new_list(a, list(reversed(a))[0])))
                else:
                    try:
                        return dict(zip(gong_reorder, config.new_list(a, gan_head)))
                    except ValueError:
                        return dict(zip(gong_reorder, config.new_list(a, self.pan_earth(option).get("坤"))))

        if fu_head_location != "中" and zhifu != "禽" and fu_head_location2 != "中":
            newlist = list(map(earth.get, rotate))
            gan_reorder = config.new_list(newlist, fu_head)
            gong_reorder = config.new_list(rotate, fu_head_location)
            if fu_head not in gan_reorder:
                start = dict(zip(config.cnumber, gan_reorder)).get(qmju[2])
                rgan_reorder = config.new_list(gan_reorder, start)
                rgong_reorder = config.new_list(gong_reorder, fu_location)
                aa = dict(zip(rgong_reorder, rgan_reorder))
                bb = dict(zip(rgan_reorder, rgong_reorder))
                return aa, bb
            if fu_head in gan_reorder:
                if fu_location is None:
                    return self.pan_earth(option)
                return {**dict(zip(gong_reorder, gan_reorder)),
                        **{"中": self.pan_earth(option).get("中")}}
        if fu_head_location != "中" and zhifu == "禽" and fu_head_location2 == "中":
            gg = list(map(earth.get, rotate))
            gan_reorder = config.new_list(gg, self.pan_earth(option).get("坤"))
            gong_reorder = config.new_list(rotate, fu_head_location)
            if fu_head not in gan_reorder:
                rgong_reorder = config.new_list(gong_reorder, fu_location)
                return dict(zip(rgong_reorder, gan_reorder))
            return {**dict(zip(gong_reorder, gan_reorder)),
                    **{"中": self.pan_earth(option)[0].get("中")}}

    # 九宮長生十二神
    def gong_chengsun(self, sky, earth):
        tianpan = {}
        dipan = {}
        for key, gan in sky.items():
            luck_mapping = config.find_shier_luck(gan)
            positions = []
            for dz in config.gong_dizhi[key]:
                if dz in luck_mapping:
                    positions.append(luck_mapping[dz])
            if len(positions) == 0 and key in luck_mapping:  # 对于中宫的处理
                positions.append(luck_mapping[key])
            if len(positions) > 0:
                if key not in tianpan:
                    tianpan[key] = {gan: positions}
                else:
                    tianpan[key][gan] = positions

        for key, gan in earth.items():
            luck_mapping = config.find_shier_luck(gan)
            positions = []
            for dz in config.gong_dizhi[key]:
                if dz in luck_mapping:
                    positions.append(luck_mapping[dz])
            if len(positions) == 0 and key in luck_mapping:  # 对于中宫的处理
                positions.append(luck_mapping[key])
            if len(positions) > 0:
                if key not in dipan:
                    dipan[key] = {gan: positions}
                else:
                    dipan[key][gan] = positions
        return {"天盤": tianpan, "地盤": dipan}

    def gong_chengsun_minute(self, option):
        def my_function(value):
            return config.find_shier_luck(value)

        def apply_function_to_dict_values(a):
            result = {}
            for key, value in a.items():
                if isinstance(value, tuple):
                    result[key] = tuple(my_function(v) for v in value)
                else:
                    result[key] = my_function(value)
            return result

        sky = config.pan_sky_minute(self.year, self.month, self.day, self.hour, self.minute)
        del sky["中"]
        gong_maping = dict(zip(config.clockwise_eightgua,
                               ["子", tuple(list("丑寅")), "卯", tuple(list("辰巳")), "午", tuple(list("未申")), "酉",
                                tuple(list("戌亥"))]))
        # Instead of creating a nested dict, make the value a tuple
        a = {k: (v, gong_maping.get(k)) for k, v in sky.items()}
        b = {k: v[0] for k, v in apply_function_to_dict_values(a).items() if v[1] is None}
        d = {}
        for key, value in gong_maping.items():
            if isinstance(value, tuple):
                d[key] = {v: b[key][v] for v in value}
            else:
                d[key] = {value: b[key][value]}
        return d

    # 六仪擊刑
    def jixing(self, sky):
        jixing_mapping = {"庚": "艮", "戊": "震", "癸": "巽", "壬": "巽", "辛": "离", "己": "坤"}
        result = {}
        for gong, gan in sky.items():
            if gan in jixing_mapping and gong == jixing_mapping[gan]:
                result[gong] = gan
        return result

    # 入墓
    def rumu(self, sky, earth):
        rumu_mapping = {"乙": "坤", "癸": "坤", "乙": "乾", "丙": "乾", "戊": "乾", "辛": "巽", "壬": "巽",
                        "丁": "艮", "己": "艮", "庚": "艮"}
        result = {}
        for gong, gan in sky.items():
            if gan in rumu_mapping and gong == rumu_mapping[gan]:
                result[gong] = gan
        for gong, gan in earth.items():
            if gan in rumu_mapping and gong == rumu_mapping[gan]:
                result[gong] = gan
        return result

    # 伏吟
    def fuying(self, star, door):
        result = {}
        if door['坎'] == '休':
            result['门伏吟'] = "是"
        elif door['坎'] == '景':
            result['门反伏吟'] = "是"

        if star['坎'] == '蓬':
            result['星伏吟'] = "是"
        elif star['坎'] == '英':
            result['星反伏吟'] = "是"

        return result

    # 门迫
    def gongpo(self, doors):
        menpo = {}
        for gong, door in doors.items():
            doorWuxing = config.door_wuxing[door]
            gongWuxing = config.gong_wuxing[gong]
            # 五行相克关系：水克火，火克金，金克木，木克土，土克水
            if doorWuxing == "水" and gongWuxing == "火":
                menpo[gong] = door
            elif doorWuxing == "火" and gongWuxing == "金":
                menpo[gong] = door
            elif doorWuxing == "金" and gongWuxing == "木":
                menpo[gong] = door
            elif doorWuxing == "木" and gongWuxing == "土":
                menpo[gong] = door
            elif doorWuxing == "土" and gongWuxing == "水":
                menpo[gong] = door
        return menpo

    # 空亡
    def kongwang(self, shunkong):
        # 提取空亡的地支
        kong_wang = list(shunkong['時空'])

        # 遍历每个宫，检查是否包含空亡的地支
        kong_wang_gong = []
        for gong, dizhi_list in config.gong_dizhi.items():
            # 检查宫的地支列表是否包含空亡的地支
            if any(dizhi in kong_wang for dizhi in dizhi_list):
                kong_wang_gong.append(gong)

        # 返回结果
        return kong_wang_gong

    # 五不遇时
    def wubuyushi(self, gz):
        ri = gz[2]
        shi = gz[3]
        mapping = {'甲': '庚午', '乙': '辛巳', '丙': '壬辰', '丁': '癸卯', '戊': '甲寅', '己': '乙丑', '庚': '丙子',
                   '辛': '丁酉', '壬': '戊申', '癸': '己未'}
        if mapping[ri[0]] == shi:
            return "是"
        else:
            return "否"

    def pan(self, option):  # 1拆補 #2置閏
        """時家奇門起盤綜合, option 1:拆補 2:置閏"""
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        gzd = "{}年{}月{}日{}時".format(gz[0], gz[1], gz[2], gz[3])
        qmju = {1: config.qimen_ju_name_chaibu(self.year,
                                               self.month,
                                               self.day,
                                               self.hour,
                                               self.minute),
                2: config.qimen_ju_name_zhirun(self.year,
                                               self.month,
                                               self.day,
                                               self.hour,
                                               self.minute)}.get(option)
        shunhead = config.shun(gz[2])
        shunkong = config.daykong_shikong(self.year,
                                          self.month,
                                          self.day,
                                          self.hour,
                                          self.minute)
        paiju = qmju
        j_q = config.jq(self.year,
                        self.month,
                        self.day,
                        self.hour,
                        self.minute)
        zfzs = config.zhifu_n_zhishi(self.year, self.month, self.day, self.hour, self.minute, option)
        pan_star_result = config.pan_star(self.year,
                                          self.month,
                                          self.day,
                                          self.hour,
                                          self.minute,
                                          option)
        star = pan_star_result[0]
        door = config.pan_door(self.year,
                               self.month,
                               self.day,
                               self.hour,
                               self.minute,
                               option)

        god = config.pan_god(self.year,
                             self.month,
                             self.day,
                             self.hour,
                             self.minute,
                             option)
        sky = self.pan_sky(option)
        earth = self.pan_earth(option)
        return {
            "排盤時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "排盤方式": {1: "拆補", 2: "置閏"}.get(option),
            "干支": gzd,
            "旬首": shunhead,
            "旬空": shunkong,
            "局日": self.qimen_ju_day(),
            "排局": paiju,
            "節氣": j_q,
            "值符值使": zfzs,
            "天乙": self.tianyi(option),
            "天盤": self.pan_sky(option),
            "地盤": self.pan_earth(option),
            "門": door,
            "星": star,
            "神": god,
            "驛馬": self.hourhorse(),
            "長生運": self.gong_chengsun(sky, earth),
            "六仪擊刑": self.jixing(sky),
            "入墓": self.rumu(sky, earth),
            "伏吟": self.fuying(star, door),
            "門迫": self.gongpo(door),
            "五不遇时": self.wubuyushi(gz),
            "空亡": self.kongwang(shunkong)
        }

    def pan_minute(self, option):
        """刻家奇門起盤綜合, option 1:拆補 2:置閏"""
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        gzd = "{}年{}月{}日{}時{}分".format(gz[0], gz[1], gz[2], gz[3], gz[4])
        s = config.multi_key_dict_get(config.liujiashun_dict(), gz[4])
        qmju = config.qimen_ju_name_ke(self.year,
                                       self.month,
                                       self.day,
                                       self.hour,
                                       self.minute)
        shunhead = config.shun(gz[3])
        shunkong = config.hourkong_minutekong(self.year,
                                              self.month,
                                              self.day,
                                              self.hour,
                                              self.minute)
        paiju = qmju
        j_q = config.jq(self.year,
                        self.month,
                        self.day,
                        self.hour,
                        self.minute)
        zfzs = config.zhifu_n_zhishi_ke(self.year,
                                        self.month,
                                        self.day,
                                        self.hour,
                                        self.minute)
        pan_star_result = config.pan_star_minute(self.year,
                                                 self.month,
                                                 self.day,
                                                 self.hour,
                                                 self.minute,
                                                 option)
        star = pan_star_result[0]
        door = config.pan_door_minute(self.year,
                                      self.month,
                                      self.day,
                                      self.hour,
                                      self.minute,
                                      option)
        god = config.pan_god_minute(self.year,
                                    self.month,
                                    self.day,
                                    self.hour,
                                    self.minute,
                                    option)
        return {
            "排盤方式": {1: "拆補", 2: "置閏"}.get(option),
            "干支": gzd,
            "旬首": shunhead,
            "旬空": shunkong,
            "局日": self.qimen_ju_day(),
            "排局": paiju,
            "節氣": j_q,
            "值符值使": zfzs,
            "天乙": self.tianyi(option),
            "天盤": config.pan_sky_minute(self.year,
                                          self.month,
                                          self.day,
                                          self.hour,
                                          self.minute),
            "地盤": config.pan_earth_minute(self.year,
                                            self.month,
                                            self.day,
                                            self.hour,
                                            self.minute),
            "門": door,
            "星": star,
            "神": god,
            "馬星": {
                "天馬": self.moonhorse(),
                "丁馬": self.dinhorse(),
                "驛馬": self.hourhorse()
            },
            # "長生運": self.gong_chengsun_minute(option),
            "暗干": dict(zip(config.angan.get(paiju[0] + paiju[2] + gz[4])[:-1], config.eight_gua)),
            "飛干": config.angan.get(paiju[0] + paiju[2] + gz[4])[-1]}

    def pan_html(self, option):
        """時家奇門html, option 1:拆補 2:置閏"""
        god = config.pan_god(self.year,
                             self.month,
                             self.day,
                             self.hour,
                             self.minute,
                             option)
        door = config.pan_door(self.year,
                               self.month,
                               self.day,
                               self.hour,
                               self.minute,
                               option)
        star = config.pan_star(self.year,
                               self.month,
                               self.day,
                               self.hour,
                               self.minute,
                               option)[0]
        sky = self.pan_sky(option)
        earth = self.pan_earth(option)
        a = ''' <div class="container"><table style="width:100%"><tr>''' + \
            "".join(['''<td align="center">''' +
                     sky.get(i) +
                     god.get(i) +
                     door.get(i) +
                     "<br>" +
                     earth.get(i) +
                     star.get(i) +
                     i + '''</td>''' for i in list("巽離坤")]) + "</tr>"
        b = ['''<td align="center">''' +
             sky.get(i) +
             god.get(i) +
             door.get(i) +
             "<br>" +
             earth.get(i) +
             star.get(i) +
             i + '''</td>''' for i in list("震兌")]
        c = '''<tr>''' + b[0] + '''<td><br><br></td>''' + b[1] + '''</tr>'''
        d = "<tr>" + \
            "".join(['''<td align="center">''' +
                     sky.get(i) +
                     god.get(i) +
                     door.get(i) +
                     "<br>" +
                     earth.get(i) +
                     star.get(i) +
                     i + '''</td>''' for i in list("艮坎乾")]) + "</tr></table></div>"
        return a + "".join(b) + c + d

    def ypan(self):
        kok = {"上元甲子": "陰一局",
               "中元甲子": "陰四局",
               "下元甲子": "陰七局"}.get(self.year_yuen()[0])
        return kok

    def gpan(self):
        j_q = config.jq(self.year,
                        self.month,
                        self.day,
                        self.hour,
                        self.minute)
        dgz = config.gangzhi(self.year,
                             self.month,
                             self.day,
                             self.hour,
                             self.minute)[2]
        dh = config.multi_key_dict_get({tuple(config.jieqi_name[0:12]): "冬至",
                                        tuple(config.jieqi_name[0:12]): "夏至"}, j_q)
        eg = "坎坤震巽乾兌艮離"
        yy = {"冬至": "陽遁", "夏至": "陰遁"}.get(dh)
        ty_doors = {"冬至": dict(zip(config.jiazi(), itertools.cycle(list("艮離坎坤震巽中乾兌")))),
                    "夏至": dict(zip(config.jiazi(), itertools.cycle(list("坤坎離艮兌乾中巽震"))))}
        gong = ty_doors.get(dh).get(dgz)
        eight_gua = list("坎坤震巽中乾兌艮離")
        rotate_order = {"陽遁": eight_gua, "陰遁": list(reversed(eight_gua))}.get(yy)
        a_gong = config.new_list(rotate_order, gong)
        gold_g = re.findall("..", "太乙攝提軒轅招搖天符青龍咸池太陰天乙")
        star_pai = dict(zip(a_gong, gold_g))
        triple_list = list(map(lambda x: x + x + x, list(range(0, 21))))
        b = list(starmap(lambda start, end: tuple(config.jiazi()[start:end]), zip(triple_list[:-1], triple_list[1:])))
        rest_door_settings = {"陽遁": dict(zip(b, itertools.cycle(eg))),
                              "陰遁": dict(zip(b, itertools.cycle(list(reversed(eg)))))}.get(yy)
        clockwise_eightgua = list("坎艮震巽離坤兌乾")
        door_r = list("休生傷杜景死驚開")
        rest = config.multi_key_dict_get(rest_door_settings, dgz)
        the_doors = {"陽遁": dict(zip(config.new_list(clockwise_eightgua, rest), door_r)),
                     "陰遁": dict(zip(config.new_list(list(reversed(clockwise_eightgua)), rest), door_r))}.get(yy)
        return {"局": yy + dgz + "日",
                "鶴神": self.crane_god().get(dgz),
                "星": star_pai,
                "門": {**the_doors,
                       **{"中": ""}},
                "神": config.getgtw().get(dgz[0])}

    # 鶴神
    def crane_god(self):
        d = list("巽離坤兌乾坎天艮震")
        dd = [6, 5, 6, 5, 6, 5, 16, 6, 5]
        newc_list = list(map(lambda i: [d[i][:5]] * dd[i], list(range(0, 8))))
        return dict(zip(config.new_list(config.jiazi(), "庚申"), newc_list))

    def gpan_html(self):
        gpan_data = self.gpan()
        door = gpan_data.get("門")
        star = gpan_data.get("星")
        html_output = '''<div class="container"><table style="width:100%"><tr>'''
        html_output += ''.join([
            f'''<td align="center">{star[i]}<br>{door[i]}{i}</td>''' for i in "巽離坤"
        ])
        html_output += "</tr><tr>"
        html_output += ''.join([
            f'''<td align="center">{star[i]}<br>{door[i]}{i}</td>''' for i in "震中兌"
        ])
        html_output += "</tr><tr>"
        html_output += ''.join([
            f'''<td align="center">{star[i]}<br>{door[i]}{i}</td>''' for i in "艮坎乾"
        ])
        html_output += "</tr></table></div>"
        return html_output

    # 天乙
    def tianyi(self, option):
        zhifu_n_zhishi = config.zhifu_n_zhishi(self.year,
                                               self.month,
                                               self.day,
                                               self.hour,
                                               self.minute,
                                               option)
        zhifu_dict = dict(zip(config.eight_gua, list("蓬芮沖輔禽心柱任英")))
        try:
            star_location = zhifu_dict.get(zhifu_n_zhishi.get("值符星宮")[1])
        except IndexError:
            star_location = "禽"
        return star_location

    # 丁馬
    def dinhorse(self):
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        tg = re.findall("..", "甲子甲戌甲申甲午甲辰甲寅")
        new_dict = dict(zip(tg, list("卯丑亥酉未巳")))
        new = config.multi_key_dict_get(config.liujiashun_dict(), gz[2])
        return config.multi_key_dict_get(new_dict, new)

    # 天馬
    def moonhorse(self):
        Gangzhi = config.gangzhi(self.year,
                                 self.month,
                                 self.day,
                                 self.hour,
                                 self.minute)
        tg = re.findall("..", "寅申卯酉辰戌巳亥午子丑未")
        new = list(map(lambda i: tuple(i), tg))
        new_dict = dict(zip(new, list("午申戌子寅辰")))
        return config.multi_key_dict_get(new_dict, Gangzhi[2][1])

    # 驛馬星
    def hourhorse(self):
        Gangzhi = config.gangzhi(self.year,
                                 self.month,
                                 self.day,
                                 self.hour,
                                 self.minute)
        tg = re.findall("...", "申子辰寅午戌亥卯未巳酉丑")
        new = list(map(lambda i: tuple(i), tg))
        new_dict = dict(zip(new, list("寅申巳亥")))

        horse = config.multi_key_dict_get(new_dict, Gangzhi[3][1])
        for gong, dizhi_list in config.gong_dizhi.items():
            if horse in dizhi_list:
                return {gong: horse}

        return None

    def green_dragon(self, option):
        """青龍返首"""
        hg = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)[3][0]
        sky = self.pan_sky(option)
        earth = self.pan_earth(option)
        zhishi = config.zhifu_n_zhishi(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            option).get("值符天干")[1]
        zf_gong = config.zhifu_n_zhishi(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            option).get("值符星宮")[1]
        zhishi_gong = bidict(earth).inverse[zhishi]
        try:
            sky_gong = bidict(sky).inverse["戊"]
            earth_gong = bidict(earth).inverse["丙"]
            if earth_gong == sky_gong:
                return {"青龍返首": sky_gong}
            if zhishi_gong == earth_gong:
                return {"青龍返首": earth_gong}
            if sky_gong == "中":
                return {"青龍返首": earth_gong}
            else:
                return {"青龍返首": "沒有"}
        except KeyError:
            if hg == "戊" or hg == "丙":
                if zhishi_gong == "中":
                    return {"青龍返首": zf_gong}
                if zf_gong == "中":
                    return {"青龍返首": bidict(sky).inverse[earth.get("坤")]}
            else:
                return {"青龍返首": "沒有"}

    def fly_bird(self, option):
        """飛鳥跌穴"""
        sky = self.pan_sky(option)
        earth = self.pan_earth(option)
        zhishi = config.zhifu_n_zhishi(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            option).get("值符天干")[1]
        zf_gong = config.zhifu_n_zhishi(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            option).get("值符星宮")[1]
        try:
            zhishi_gong = bidict(earth).inverse[zhishi]
            earth_gong = bidict(earth).inverse["戊"]
            sky_gong = bidict(sky).inverse["丙"]
            if earth_gong == sky_gong:
                return {"飛鳥跌穴": sky_gong}
            if sky_gong == zhishi_gong:
                return {"飛鳥跌穴": sky_gong}
            else:
                return {"飛鳥跌穴": "沒有"}
        except (KeyError, AttributeError):
            if zhishi_gong == "中":
                return {"飛鳥跌穴": config.zhifu_n_zhishi(
                    self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    option).get("值符星宮")[1]}
            else:
                return {"飛鳥跌穴": "沒有"}

    def jade_girl(self, option):
        """玉女守門"""
        earth = self.pan_earth(option)
        try:
            earth_gong = bidict(earth).inverse["丁"]
            zhishi = config.zhifu_n_zhishi(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                option).get('值使門宮')[1]
            if zhishi == earth_gong:
                return {"玉女守門": zhishi}
            else:
                return {"玉女守門": "沒有"}
        except KeyError:
            return {"玉女守門": "沒有"}

    def tianhen(self, option):
        """天顯時格"""
        gz = config.gangzhi(self.year,
                            self.month,
                            self.day,
                            self.hour,
                            self.minute)
        dgz = gz[2]
        hgz = gz[3]

        return

    def overall(self, option):
        """整體奇門起盤綜合, option 1:拆補 2:置閏"""
        return {"金函玉鏡(日家奇門)": self.gpan(),
                "時家奇門": self.pan(option),
                "刻家奇門": self.pan_minute(option)}


import argparse
from flask import Flask, request, jsonify
import json
from zhconv import convert

@app.route('/qimen', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        y = request.args.get('year', type=int, default=datetime.now().year)
        m = request.args.get('month', type=int, default=datetime.now().month)
        d = request.args.get('day', type=int, default=datetime.now().day)
        h = request.args.get('hour', type=int, default=datetime.now().hour)
        f = request.args.get('minute', type=int, default=datetime.now().minute)
        n = request.args.get('number', type=int, default=1)
        r = request.args.get('random', type=int, default=-1)
    else:  # POST
        data = request.get_json()
        y = data.get('year',datetime.now().year)
        m = data.get('month',datetime.now().month)
        d = data.get('day',datetime.now().day)
        h = data.get('hour',datetime.now().hour)
        f = data.get('minute',datetime.now().minute)
        n = data.get('number',1)
        r = data.get('random',-1)
    if r != -1:
        random.seed(r)
        y = int(random.randint(2000, 3000))
        m = int(random.randint(1, 12))
        d = int(random.randint(1, 30))
        h = int(random.randint(0, 23))
        f = int(random.randint(0, 59))

    result = Qimen(y, m, d, h, f).pan(n)
    response = convert(json.dumps(result, ensure_ascii=False),'zh-cn')
    print(response)
    return response

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
