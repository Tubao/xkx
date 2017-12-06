# -*- coding: utf-8 -*-
import sys
from mydb import getconn


def main(args):
#    area = "xkt;ddj;em;qfa;fds;fz;gb;gm;ha;ms;xt;gjc;gw;yinz;gy;hanz;hz;hmy;hhh;hyd;bs;hs;cll;xc;hb;hb1;hb2;hb3;hb4;hn1;hn2;hn3;hn4;jx;jyg;jmg;jz;jy;jzh;km;fd;lld;llx;lj;dzt;lz;lxc;ljz;ly;ll;mt;mz;mlb;mlx;mj;mgk;mr;mrf;nc;ny;px;pyh;py;qlc;qy;qhb;qhn;qf;qq;qzh;qz;ry;rbz;rz;ssb;lvz;shg;fzl;sl;sld;fengd;sy;skf;sdb;sdn;sz;taih;tais;dzf;tgk;th;tyc;ty;tdh;tls;tzf;tz;tx;wat;wjg;gd;wl;yb;wd;wdc;wm;wys;xyz;xy;xf;xz;xiny;xx;txg;xch;xs;ys;yzw;yz;yiz;yg;ywm;yy;zp;zjk;zz;ca;jb1;jb2;jb3;jb4;jn1;jn2;jn3;jn4;zj;zx;zf;tdf;xh;hsz;jnqz;hzbs;zuo;ct;qiu;kf;bofu;fm;fh;ht;tf;tt;hst;cym;scm;zjc;sd;kd;jk;lanz;huangz"
#    cname="大轮谢客亭;都大锦;峨嵋;峨嵋千佛庵;发呆室;福州;丐帮;古墓;古墓河岸;古墓密室;古墓小厅;挂剑祠;关外;归云隐者;归云庄;汉中;杭州;黑木崖;红花会;胡一刀;花园别墅区;华山;华山苍龙岭;华山村;淮北;黄河渡口北1;黄河渡口北2;黄河渡口北3;黄河渡口北4;黄河渡口南1;黄河渡口南2;黄河渡口南3;黄河渡口南4;嘉兴;嘉峪关;剑门关;江州;晋阳;荆州;昆明;琅缳福地;老林东;老林西;灵鹫;灵鹫独尊厅;灵州;凌霄城;陆家庄;洛阳;绿柳山庄;曼陀山庄;梅庄;苗岭北;苗岭西;明教;莫高窟;慕容;慕容复;南昌;南阳;平西王府;鄱阳湖;濮阳;麒麟村;琴韵小筑;青海湖北;青海湖南;曲埠;曲清;全真教;泉州;日月神教;荣宝斋;汝州;杀手帮;沙漠绿洲;山海关;少林方丈楼;少林寺;神龙岛;神龙峰顶;神龙山腰;史可法;蜀道北;蜀道南;苏州;太湖;泰山;泰山岱宗坊;塘沽口;桃花岛;桃园村;桃源;天地会;天龙寺;天柱峰;铁掌峰;听香水榭;万安塔;万劫谷;无量谷底;无量山;无量玉璧;武当;武当村;武庙;武夷山;戏园子;襄阳;萧峰;小镇;信阳;星宿;星宿天秀宫;许昌;雪山派;牙山;燕子坞;扬州;驿站;瑛姑;岳王墓;岳阳;赞普;张家口;张志;长安;长江渡口北1;长江渡口北2;长江渡口北3;长江渡口北4;长江渡口南1;长江渡口南2;长江渡口南3;长江渡口南4;镇江;朱熹;庄府;提督府;西湖;韩世忠;江南钱庄;杭州别墅;昌隆镖局;朝廷;裘千丈;康亲王府;钵夫;飞马镖局;飞虎镖局;后堂;天福镖局;丹陛桥;洪水坛;朝阳门;神策门;端门;树洞内部;客店;建康府;兰州;湟中"
#    ctname="谢客亭;龙门镖局;玉女池;千佛庵大殿;发呆室;福威镖局;土地庙;断龙石;河岸;密室;小厅;挂剑祠;集市;隐者居;归云亭;汉中;大理寺;成德殿;杭州分舵大门;高粱地;花园别墅区;书房;苍龙岭;打谷场;淮北;无;风陵渡;无;无;无;孟津渡;无;无;嘉兴城;嘉峪关;剑门关;韩家;萧府;荆州;神威镖局;琅缳福地;老林尽头;老林边缘;百丈涧;独尊厅大门;皇宫大门;凌霄大厅;陆家庄;洛阳中心广场;绿柳山庄大门;小桥;梅庄天井;无;无;半山门;莫高窟;湖边;春来茶馆;白家;南阳城;平西王府大门;鄱阳湖边;濮阳;岳飞家;琴韵小居;黄羊滩;无;孔庙;荣昌交易行;崇玄台;泉州港;小村庄;荣宝斋;汝州城;万纶台;沙漠绿洲;山海关南门;方丈楼;少林寺;海滩;峰顶;小回廊;城北军营;无;无;宝带桥;太湖边;南天门;岱宗坊;塘沽口;海港;桃园小路;桃源驿站;侧厅;瑞鹤门;天柱峰下;小亭;听香水榭;万安塔;万劫谷;谷底;崖间古松;无量玉璧;武当广场;武当山门;武庙;武夷山路;戏园子;襄阳当铺;望星楼二层;小镇;镇淮桥;巨岩;天秀宫;许昌城;桥头;牙山湾中心;燕子坞大门;中央广场;驿站;黑沼小屋;墓前广场;南门内大街;赞普广场;大境门;荆西镖局;朱雀门;扬子津;无;无;无;无;采石矶;无;无;梦溪园;岳麓书院;庄府大门;提督府正门;孤山;大厅;江南钱庄;无;昌隆镖局;厅堂;望江亭;王府大门;殿前广场;飞马镖局;飞虎镖局;后堂;天福镖局;丹陛桥;洪水坛;朝阳门;神策门;端门;树洞内部;客店;中城;府前广场;宫城"
#    area_list = area.split(";")
#    cname_list = cname.split(";")
#    ctname_list = ctname.split(";")
#    size = len(area_list)
#    conn = getconn()
#    cursor = conn.cursor()
#    for i in range(size):
#        cursor.execute('insert into areainfo(aid,xy_ename,cname,ct_cname) values(?,?,?,?)',(area_list[i].decode("utf8"),area_list[i].decode("utf8"),cname_list[i].decode("utf8"),ctname_list[i].decode("utf8")))
#    conn.commit()
#    conn.close()
    words = ""
    
    conn = getconn()
    cursor = conn.cursor()
       
if __name__=="__main__":
    main(sys.argv)
