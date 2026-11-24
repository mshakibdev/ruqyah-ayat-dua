# পাইপলাইন — প্রোটোকল PDF থেকে সংকলন JSON

মূল PDF-গুলোর **আরবি টেক্সট লেয়ার ভাঙা** (অক্ষর ও যের-যবর উল্টে আসে) আর
**বাংলায় শব্দের ভেতরে ফাঁক** ঢুকে যায় ("নিয় ত" = "নিয়ত")। তাই:

| অংশ | কোথা থেকে আসে |
|---|---|
| আয়াতের আরবি | উসমানী হাফস মুসহাফ — `hafs.json` |
| আয়াতের বাংলা অর্থ | মুহিউদ্দীন খানের অনুবাদ — `bn-mkhan.json` |
| পাঠসংখ্যা | PDF (সংখ্যা ভাঙে না) |
| নিয়ত | PDF, তারপর `niyat_fix.json`-এ হাতে মিলিয়ে নেওয়া পাঠ |
| দোয়ার আরবি | পাতার ছবি দেখে হাতে — `assemble.py`-তে |

## তথ্যভাণ্ডার নামানো

রিপো হালকা রাখতে বড় দুটি ফাইল এখানে রাখা হয়নি:

```bash
pip download --no-deps -d /tmp/q quran-text
unzip -o /tmp/q/quran_text-*.whl -d /tmp/qx
cp /tmp/qx/quran_text_data/hafs.json .

curl -o bn-mkhan.json \
  https://raw.githubusercontent.com/fawazahmed0/quran-api/1/editions/ben-muhiuddinkhan.json
```

## চালানো

```bash
python3 extract_protocol.py <নথি>.pdf > ../draft/<নাম>.json   # আয়াত বের করা
python3 assemble.py                                            # সংকলন JSON বানানো
cd .. && python3 gen_ayat_app.py                               # পাতা তৈরি
```

`despace.py` — PDF-এর বাংলা থেকে ভুল ফাঁক সরায়। সিদ্ধান্ত নেয় শব্দের
**কম্পাঙ্ক** দেখে: "সু" অনুবাদে দু-একবার এলেও শব্দ নয়, তাই "সু রক্ষা" জোড়া লাগে;
"সাড়া" ও "দেওয়া" দুটোই পাকা শব্দ, তাই ওদের ফাঁক থাকে।
