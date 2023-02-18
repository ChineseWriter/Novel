from novel import Book, Chapter, StorageServer


b= Book("", "", Book.BookState.END, "", "")
for i in range(0, 10000):
    c = Chapter("", i, str(i), "", "a")
    b.append(c)

StorageServer(b, StorageServer.StorageMethod.TXT_MANY_FILE).save()