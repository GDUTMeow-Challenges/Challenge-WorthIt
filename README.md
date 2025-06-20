# Challenge-WorthIt

## 构建说明

```bash
$ docker build . -t challenge-worthit
```

如果要代理的话

```bash
$ docker build . -t challenge-worthit --build-arg HTTP_PROXY="http://host.docker.internal:10809" --build-arg HTTPS_PROXY="http://host.docker.internal:10809"
```

开启容器时需要传入环境变量 `FLAG`
