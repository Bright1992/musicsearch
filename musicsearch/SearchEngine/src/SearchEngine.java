/**
 * Created by frank on 17-5-22.
 */
import com.sun.javaws.exceptions.InvalidArgumentException;
import javafx.util.Pair;
import org.apache.lucene.analysis.*;
import org.apache.lucene.document.*;
import org.apache.lucene.index.*;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.search.highlight.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;
import org.wltea.analyzer.lucene.IKAnalyzer;

import java.io.*;
import java.util.*;
import java.lang.Character;

public class SearchEngine
{
  private final String FieldId = "id";
  private final String FieldSong = "song";
  private final String FieldSinger = "singer";
  private final String FieldLrc = "lrc";
  private final String FieldAll = "all";
  private final String FieldPublishTime = "publishTime";
  private final String FieldPopularity = "popularity";
  private final String ActionUpdate = "update";

  private final double songThreshold=5;

  private final double lrcThreshold = 0.5;

  class MyDoc
  {
    public MyDoc(ScoreDoc sd, Query q, String fieldName, String fieldValue) throws Exception
    {
      score = sd.score;
      doc = indexSearcher.doc(sd.doc);

      setField(fieldName, fieldValue, q);

      id = Integer.valueOf(doc.get(FieldId));
      song = doc.get(FieldSong);
      singer = doc.get(FieldSinger);
      lrc = doc.get(FieldLrc);
      publishTime = Double.valueOf(doc.get(FieldPublishTime));
      popularity = Double.valueOf(doc.get(FieldPopularity));
    }

    public MyDoc(MyDoc lhs, MyDoc rhs) throws Exception
    {
      assert (lhs.id == rhs.id);

      score = lhs.score * rhs.score;
      doc = lhs.doc;

      setField(lhs);
      setField(rhs);

      id = lhs.id;
      song = lhs.song;
      singer = lhs.singer;
      lrc = lhs.lrc;
      publishTime = lhs.publishTime;
      popularity = lhs.popularity;
    }

    public MyDoc(MyDoc d, double newSore) throws Exception
    {
      score = newSore;
      doc = d.doc;

      setField(d);

      id = d.id;
      song = d.song;
      singer = d.singer;
      lrc = d.lrc;
      publishTime = d.publishTime;
      popularity = d.popularity;
    }

    public void setField(String fieldName, String fieldValue, Query query) throws Exception
    {
      QueryParser parser = new QueryParser(Version.LUCENE_40, fieldName, analyzer);
      switch (fieldName) {
        case FieldSong:
          songQueried = true;
          songQueryValue = songQueryValue+ " "+ fieldValue;
          songQuery = parser.parse(songQueryValue);
          break;

        case FieldSinger:
          singerQueried = true;
          singerQueryValue = singerQueryValue +" "+ fieldValue;
          singerQuery = parser.parse(singerQueryValue);
          break;

        case FieldLrc:
          lrcQueried = true;
          lrcQueryValue = lrcQueryValue+ " "+ fieldValue;
          lrcQuery = parser.parse(lrcQueryValue);
      }
    }

    public void setField(MyDoc doc) throws Exception
    {
      if (doc.songQueried) {
        QueryParser parser = new QueryParser(Version.LUCENE_40, FieldSong, analyzer);
        songQueried = true;
        songQueryValue = songQueryValue+" "+doc.songQueryValue;
        songQuery = parser.parse(songQueryValue);
      }
      if (doc.singerQueried) {
        QueryParser parser = new QueryParser(Version.LUCENE_40, FieldSong, analyzer);
        singerQueried = true;
        singerQueryValue = singerQueryValue+" "+ doc.singerQueryValue;
        singerQuery = parser.parse(singerQueryValue);
      }
      if (doc.lrcQueried) {
        QueryParser parser = new QueryParser(Version.LUCENE_40, FieldSong, analyzer);
        lrcQueried = true;
        lrcQueryValue = lrcQueryValue+" "+ doc.lrcQueryValue;
        lrcQuery = parser.parse(lrcQueryValue);
      }
    }

    @Override
    public String toString()
    {
      String hSong = null;
      String hSinger = null;
      String hLrc = null;

      if (songQueried) {
        hSong = highlightFiledValue(songQuery, FieldSong, song, 2000);
      }
      if (singerQueried) {
        hSinger = highlightFiledValue(singerQuery, FieldSinger, singer, 2000);
      }
      if (lrcQueried) {
        hLrc = highlightFiledValue(lrcQuery, FieldLrc, lrc);
      }

      String ret = String.format("id: %d\r\n", id);
      ret += String.format("song: %s\r\n", hSong != null ? hSong : song);
      ret += String.format("singer: %s\r\n", hSinger != null ? hSinger : singer);
      if (hLrc != null) {
        ret += String.format("lrc: %s\r\n", hLrc);
      }

      return ret;
    }

    public double score;
    public Document doc;

    public boolean songQueried = false;
    public String songQueryValue="";
    public Query songQuery;

    public boolean singerQueried = false;
    public String singerQueryValue="";
    public Query singerQuery;

    public boolean lrcQueried = false;
    public String lrcQueryValue="";
    public Query lrcQuery;

    public int id;
    public String song;
    public String singer;
    public String lrc;
    public double publishTime;
    public double popularity;
  }

  private static SearchEngine singleton;

  public static SearchEngine instance()
  {
    try {
      if (singleton == null) {
        singleton = new SearchEngine();
      }
    }catch (Exception e) {
      e.printStackTrace();
    }

    return singleton;
  }

  private SearchEngine() throws Exception
  {
    analyzer = new IKAnalyzer(true);
    directory = new SimpleFSDirectory(new File("./index"));
    directoryReader = DirectoryReader.open(directory);
    indexSearcher = new IndexSearcher(directoryReader);
    clickTimes = new HashMap<>();
    singers = new HashSet<>();

    BufferedReader reader =
            new BufferedReader(
                    new InputStreamReader(
                            new FileInputStream("src/singer.dic")));

    try {
      while (true) {
        String s = reader.readLine().toLowerCase();
        if (!s.isEmpty()) {
          singers.add(s);
        }
      }
    }
    catch (Exception e) {
      System.out.println(singers.size() + " singers");
    }

    System.out.println(directoryReader.numDocs() + " docs in search engine");
  }

  public void update(int songId, int times)
  {
    System.out.printf("update %d %d times\n", songId, times);
    clickTimes.put(songId, times);
  }

  public String search(String input)
  {
    Vector<Pair<String, String>> query = parseQuery(input);
    MyDoc[] docs = null;

    try {
      for (Pair<String, String> p : query) {
        String key = p.getKey().toLowerCase().trim();
        String value = p.getValue().toLowerCase().trim();
        MyDoc[] newDocs = null;
        switch (key) {

          case ActionUpdate:
            String[] s = value.split("[ |\t]");
            if (s.length != 2) {
              throw new InvalidArgumentException(null);
            }
            update(Integer.valueOf(s[0]), Integer.valueOf(s[1]));
            break;

          case FieldId:
          case FieldSong:
          case FieldSinger:
          case FieldLrc:
            newDocs = searchField(key, value);
            break;

          case FieldAll:
            value=value.replace(",", " ");
            String [] values=value.split(" ");
            MyDoc[] cur_docs=null;
            for(String v : values) {
              if (singers.contains(v)) {
                // 优先从词典中匹配歌手名
                newDocs = searchField(FieldSinger, v);
                System.out.printf("hits %d\n", newDocs.length);
              } else {
                // 歌名 & singer
                newDocs=searchField(FieldSinger,v);
                newDocs = unionDocs(searchField(FieldSong,v),newDocs);
                sortDocs(newDocs);
                System.out.printf("hits %d\n", newDocs.length);
                if (newDocs.length > 0) {
                  System.out.printf("song score %f \n", newDocs[0].score);
                }
                if (newDocs.length == 0) {
                  // 歌词优先级最低
                  newDocs = searchField(FieldLrc, v);
                  sortDocs(newDocs);
                  System.out.printf("hits %d\n", newDocs.length);
                  if (newDocs.length > 0) {
                    System.out.printf("lrc score %f \n", newDocs[0].score);
                  }
                }
              }
              if(cur_docs==null)
                cur_docs=newDocs;
              else
                cur_docs=intersectDocs(cur_docs,newDocs);
            }
            newDocs=cur_docs;
            break;

          default:
            throw new InvalidArgumentException(null);
        }

        if (docs == null) {
          docs = newDocs;
        } else {
          docs = intersectDocs(docs, newDocs);
        }
      }
    }
    catch (Exception e) {
      e.printStackTrace();
    }

    if (docs == null) {
      docs = new MyDoc[0];
    }

    sortDocs(docs);
    StringBuilder buf = new StringBuilder(128);
    buf.append(String.format("hits: %d\r\n\r\n", docs.length));
    for (MyDoc d : docs) {
      buf.append(d.toString());
      buf.append("\r\n");
    }
//    System.out.println(buf.toString());
    return buf.toString();
  }

  private Vector<Pair<String, String>> parseQuery(String input)
  {
    BufferedReader reader =
            new BufferedReader(new StringReader(input));
    Vector<Pair<String, String>> ret = new Vector<>(1);

    try {
      while (true) {
        String line = reader.readLine();
        if (line == null) {
          break;
        }

        String[] pair = line.split(":");
        if (pair.length != 2) {
          throw new IOException("invalid query");
        }

        pair[0] = pair[0].trim();
        pair[1] = pair[1].trim();

        if (pair[0].equalsIgnoreCase(FieldSong)) {
          pair[0] = FieldSong;
        }
        else if (pair[0].equalsIgnoreCase(FieldSinger)) {
          pair[0] = FieldSinger;
        }
        else if (pair[0].equalsIgnoreCase(FieldLrc)) {
          pair[0] = FieldLrc;
        }
        else if (pair[0].equalsIgnoreCase(FieldAll)) {
          pair[0] = FieldAll;
        }
        else if (pair[0].equalsIgnoreCase(ActionUpdate)) {
          pair[0] = ActionUpdate;
        }

        else {
          throw new IOException("invalid query");
        }
        ret.add(new Pair<>(pair[0], pair[1]));
      }
    }
    catch (Exception e) {
      e.printStackTrace();
    }

    return ret;
  }

  private boolean isLatin(String str){
    for(int i=0;i<str.length();++i){
      int cp=str.codePointAt(i);
      if(cp>127)
        return false;
    }
    return true;
  }

  private MyDoc[] searchField(String name, String value) throws Exception
  {
    QueryParser parser = new QueryParser(Version.LUCENE_40, name, analyzer);
    Query query = parser.parse(value);
    int n=100;
    if(name=="singer"||name=="song")
      n=500;
    ScoreDoc[] sdocs = indexSearcher.search(query, 500).scoreDocs;
    MyDoc[] mdocs = new MyDoc[sdocs.length];
    int hits=0;
    double thres=0;
    switch (name){
      case "song":
        if(isLatin(value))
          thres=0;
        else
          thres=songThreshold;
        break;
      case "lrc":
        thres=lrcThreshold;
        break;
      default:
        thres = 0;
    }

    for (int i = 0; i < mdocs.length; ++i) {
      if(sdocs[i].score>=thres) {
        hits += 1;
        mdocs[i] = new MyDoc(sdocs[i], query, name, value);

        int id = mdocs[i].id;
        int times = clickTimes.getOrDefault(id, 0);

        mdocs[i].score = sdocs[i].score * (1 + Math.log(1 + times));
      }
    }
    MyDoc[] mdocs2=new MyDoc[hits];
    for(int i=0;i<hits;++i)
      mdocs2[i]=mdocs[i];
    System.out.println(query);
    return mdocs2;
  }

  private String highlightFiledValue(Query q, String fieldName, String text){
    return highlightFiledValue(q,fieldName,text,50);
  }

  private String highlightFiledValue(Query q, String fieldName, String text,int fragSize)
  {
    SimpleHTMLFormatter simpleHTMLFormatter =
            new SimpleHTMLFormatter(
                    "<font color=\"#FF0000\">", "</font>");

    Highlighter highlighter =
            new Highlighter(simpleHTMLFormatter, new QueryScorer(q));

    highlighter.setTextFragmenter(new SimpleFragmenter(fragSize));

    try {
      return highlighter.getBestFragment(analyzer, fieldName, text);
    }
    catch (Exception e) {
      e.printStackTrace();
    }
    return "";
  }

  private void sortDocs(MyDoc[] docs)
  {
        /* 根据score, popularity, publishTime排序 */
    class MyComparator implements Comparator<MyDoc>
    {
      public int compare(MyDoc lhs, MyDoc rhs)
      {
        if (lhs.score != rhs.score) {
          return lhs.score < rhs.score ? 1 : -1;
        }

        if (lhs.popularity != rhs.popularity) {
          return lhs.popularity < rhs.popularity ? -1 : 1;
        }

        if (lhs.publishTime!=rhs.publishTime)
          return lhs.publishTime > rhs.publishTime ? -1 : 1;

        return 0;
      }
    }
    Arrays.sort(docs, new MyComparator());
  }

  private int nToken(String input) throws Exception
  {
    int tokens = 0;
    TokenStream ts = analyzer.tokenStream("myfield", new StringReader(input));

    //重置TokenStream（重置StringReader）
    ts.reset();

    //迭代获取分词结果
    while (ts.incrementToken()) {
      ++tokens;
    }

    //关闭TokenStream（关闭StringReader）
    ts.end();

    return tokens;
  }

  private MyDoc[] intersectDocs(MyDoc[] a, MyDoc[] b) throws Exception
  {
    Vector<MyDoc> vec = new Vector<>();
    for (MyDoc d1 : a) {
      for (MyDoc d2 : b) {
        if (d1.id == d2.id) {
          vec.add(new MyDoc(d1, d2));
        }
      }
    }

    MyDoc[] arr = new MyDoc[vec.size()];
    return vec.toArray(arr);
  }

  private MyDoc[] unionDocs(MyDoc[] a, MyDoc[] b) throws Exception
  {
    Vector<MyDoc> vec = new Vector<>();
    Collections.addAll(vec, b);
    for (MyDoc d1 : a) {
      boolean found = false;
      for (MyDoc d2 : b) {
        if (d1.id == d2.id) {
          found = true;
          d1=new MyDoc(d1,d2);
          break;
        }
      }
      if (!found) {
        vec.add(d1);
      }
    }
    MyDoc[] arr = new MyDoc[vec.size()];
    return vec.toArray(arr);
  }

  private HashSet<String> singers;
  private Analyzer analyzer;
  private Directory directory;
  private DirectoryReader directoryReader;
  private IndexSearcher indexSearcher;
  private HashMap<Integer, Integer> clickTimes;

  public static void main(String[] args) throws Exception
  {
    SearchEngine se = new SearchEngine();
    BufferedReader reader =
            new BufferedReader(
                    new InputStreamReader(System.in));

    String input = "singer: 周杰伦\r\nsong: 搁浅\r\n";
    se.search(input);

    while (true) {

      System.out.print("search: ");
      input = reader.readLine();

      System.out.println(se.search(input));

      //System.out.print("click: ");
      //int click = Integer.valueOf(reader.readLine());
      //se.update(click);
    }
  }
}