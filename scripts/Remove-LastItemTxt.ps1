Param(
    $Path = ""
)
$stream = [IO.File]::OpenWrite($Path)
$stream.SetLength($stream.Length - 2)
$stream.Close()
$stream.Dispose()