# pdf2cbz

## build

```bash
docker image build -t pdf2cbz .
```

## run

カレントディレクトリに xxxx.pdf を配置して以下の通り実行する。
カレントディレクトリのバインドマウント先は /data とする。

```bash
docker run -t -v ${PWD}:/data pdf2cbz convert xxxx.pdf -h 2048
```
