# Comparison with similar packages

Some other packages have similar functionality as `checkpointing`.
However we handle some cases better than them, as explained below.

## cachier

The following cases are tested with
[cachier](https://github.com/shaypal5/cachier) version 1.5.4.

### Code change

cachier does not watch the function code at all,
therefore, if the code logic has changed, it will not rerun which leads to wrong result.






