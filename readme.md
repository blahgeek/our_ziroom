# Our Ziroom

用来结合百度地图找适合两（多）个人的自如房子。

## Usage

先从[百度地图](http://lbsyun.baidu.com/apiconsole/key)搞一个API Key。

```bash
cd ziroom
# (optional) rm -rf .scrapy/httpcache
scrapy crawl ziroom -o data.json

cd ..
python3 finder.py \
    --max-price 5000 \
    --tag 独卫 \
    --tag 独立阳台 \
    --distance 五道口地铁站,50 \
    --distance 国贸地铁站,50 \
    --ak xxxxxxxxxxxxxxxxxxxxxxxxx \
    ziroom/data.json
```

详情：`python3 finder.py -h`
