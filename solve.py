import json
import os

from bs4 import BeautifulSoup
import pandas as pd

def main():
    os.makedirs("output", exist_ok=True)

    with open("result.json", "r") as fb:
        data = json.loads(fb.read())

    aqi_data = {}
    weather_data = {}

    for key, value in data.items():
        if "aqi" in key:
            aqi_data[key] = value
        else:
            weather_data[key] = value

    # AQI
    for key, value in aqi_data.items():
        soup = BeautifulSoup(value, 'html.parser')
        # Get data area
        d = soup.find("div", id="content").select(".api_month_list")[0].table.select("tr")

        # Head
        head = [str(i).strip("<td>\n<b>").strip("</b></td>") for i in d[0].select("td")]
        df = pd.DataFrame([], columns=head)

        for fd in d[1:]:
            fds = fd.select("td")

            detail = []
            for i in fds:
                temp = str(i)\
                    .replace("</td>", "").replace("<td>", "")\
                    .replace('<td class="aqi-lv1">\r\n', "")\
                    .replace('<td class="aqi-lv2">\r\n', "")\
                    .replace('<td class="aqi-lv3">\r\n', "")\
                    .replace('<td class="aqi-lv4">\r\n', "")\
                    .replace('<td class="aqi-lv5">\r\n', "")\
                    .replace('<td class="aqi-lv6">\r\n', "")\
                    .strip()
                try:
                    temp = float(temp)
                except:
                    pass
                detail.append([temp])
            

            df = df.append(pd.DataFrame(dict(zip(
                head, detail
            ))), ignore_index=True)

        name = int(key\
            .replace('http://tianqihoubao.com/aqi/jiaxing-', "")\
            .replace(".html", ""))
        
        os.makedirs(os.path.join("output", f"{name // 100}"), exist_ok=True)
        path = os.path.join("output", f"{name // 100}", "{}月.xls".format(name % 100))
        print(f"{path} Done")
        df.to_excel(path)

    # Weather
    for key, value in weather_data.items():
        soup = BeautifulSoup(value, 'html.parser')
        # Get data area
        d = soup.find("div", id="content").select(".b")[0].select("tr")

        # Head
        head = [str(i).strip("<td>\n<b>").strip("</b></td>") for i in d[0].select("td")]
        df = pd.DataFrame([], columns=head)

        for fd in d[1:]:
            fds = fd.select("td")

            detail = []
            for i in fds:
                if "年" in str(i):
                    temp = str(i)[115:].strip("</td>").strip().strip("</a>").strip()
                elif "/" in str(i):
                    temp = str(i).strip().strip("<td>").strip("</td>").strip().replace(" ", "").replace("\r\n", "").split("/")
                else:
                    temp = str(i)

                if type(temp) is list:
                    temp = [i.replace("&lt;", "<").replace("～", "-") for i in temp]
                else:
                    temp = temp.replace("&lt;", "<").replace("～", "-")
                
                if type(temp) is list and "℃" in temp[0]:
                    temp = [int(i.replace("℃", "")) for i in temp]
                detail.append([temp])
            

            df = df.append(pd.DataFrame(dict(zip(
                head, detail
            ))), ignore_index=True)

        df["天气1"] = [""] * len(df.index)
        df["天气2"] = [""] * len(df.index)
        for i in range(len(df.index)):
            df.loc[i, "天气1"] = df.at[i, "天气状况"][0]
            df.loc[i, "天气2"] = df.at[i, "天气状况"][1]
        df = df.drop(labels='天气状况', axis=1)

        df["最高气温"] = [""] * len(df.index)
        df["最低气温"] = [""] * len(df.index)
        for i in range(len(df.index)):
            df.loc[i, "最低气温"] = int(df.at[i, "最低气温/最高气温"][0])
            df.loc[i, "最高气温"] = int(df.at[i, "最低气温/最高气温"][1])
        df = df.drop(labels='最低气温/最高气温', axis=1)

        df["白天风向"] = [""] * len(df.index)
        df["夜晚风向"] = [""] * len(df.index)
        df["白天风力1"] = [""] * len(df.index)
        df["白天风力2"] = [""] * len(df.index)
        df["夜晚风力1"] = [""] * len(df.index)
        df["夜晚风力2"] = [""] * len(df.index)
        for i in range(len(df.index)):
            if "无持续" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "无持续" not in str(df.at[i, "风力风向(夜间/白天)"][1]) :
                if "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[1])
                elif "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" not in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                elif "-" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[1])
                else:
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
            elif "无持续" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "无持续" in str(df.at[i, "风力风向(夜间/白天)"][1]) :
                if "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[1])
                elif "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" not in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                elif "-" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[1])
                else:
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
            elif "无持续" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "无持续" not in str(df.at[i, "风力风向(夜间/白天)"][1]) :
                if "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[1])
                elif "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" not in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                elif "-" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "").split("-")[1])
                else:
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风")[1].replace("级", "")
            else:
                if "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[1])
                elif "-" in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" not in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = int(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "").split("-")[1])
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                elif "-" not in str(df.at[i, "风力风向(夜间/白天)"][0]) and "-" in str(df.at[i, "风力风向(夜间/白天)"][1]):
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[0])
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = int(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "").split("-")[1])
                else:
                    df.loc[i, "白天风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][0].split("风向")[0])
                    df.loc[i, "夜晚风向"] = "{}风".format(df.at[i, "风力风向(夜间/白天)"][1].split("风向")[0])
                    df.loc[i, "白天风力1"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力1"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")
                    df.loc[i, "白天风力2"] = df.at[i, "风力风向(夜间/白天)"][0].split("风向")[1].replace("级", "")
                    df.loc[i, "夜晚风力2"] = df.at[i, "风力风向(夜间/白天)"][1].split("风向")[1].replace("级", "")

        df = df.drop(labels='风力风向(夜间/白天)', axis=1)

        name = int(key\
            .replace('http://www.tianqihoubao.com/lishi/jiaxing/month/', "")\
            .replace(".html", ""))

        os.makedirs(os.path.join("output", f"{name // 100}"), exist_ok=True)
        path = os.path.join("output", f"{name // 100}", "{}月.xls".format(name % 100))
        if os.path.exists(path):
            df_o = pd.read_excel(path)
            df_c = pd.merge(df, df_o)

            for i in df_o.columns:
                df_c[i] = df_o[i]

            for i in range(len(df.index)):
                for j in range(len(df_c.index)):
                    year = str(df.at[i, "日期"]).split("年")[0]
                    month = str(df.at[i, "日期"]).split("年")[1].split("月")[0]
                    day = str(df.at[i, "日期"]).split("年")[1].split("月")[1].replace("日", "")
                    if len(month) == 1:
                        month = f"0{month}"
                    if len(day) == 1:
                        day = f"0{day}"

                    if str(df_c.at[j, "日期"]) == "{}-{}-{}".format(year, month, day):
                        for k in df.columns:
                            if str(k) != "日期":
                                df_c.loc[j, str(k)] = df.at[i, str(k)]
            
            df_c = df_c.drop(labels="Unnamed: 0", axis=1)

            print(f"{path} Done")
            df_c.to_excel(path)
        else:
            print(f"{path} Done")
            df.to_excel(path)


if __name__ == "__main__":
    main()