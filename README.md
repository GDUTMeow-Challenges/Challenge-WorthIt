# Challenge-WorthIt

Luminoria 使用 Notion 数据库做了一个网站，来记录自己买过的东西，以至于太喜欢这个网站了，在网站上添加了一个「呼叫」按钮，点击它，Luminoria 就会回来看一下自己的网站，就好像在看一件艺术品

## 构建说明

```bash
$ docker build . -t challenge-worthit
```

如果要代理的话

```bash
$ docker build . -t challenge-worthit --build-arg HTTP_PROXY="http://host.docker.internal:10809" --build-arg HTTPS_PROXY="http://host.docker.internal:10809"
```

开启容器时需要传入环境变量 `FLAG`
