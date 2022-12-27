import aiohttp


class AsyncHttpSession:
    _session = None

    async def shutdown(self):
        """Метод завершения соединения"""
        self._session.close()

    def client(self, timeout: int):
        """Получение клиента"""
        if self._session is None:
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=timeout)
            self._session = aiohttp.ClientSession(
                connector=connector, timeout=timeout
            )

        return self._session


http_session: AsyncHttpSession = AsyncHttpSession()


async def get_http_session() -> AsyncHttpSession | None:
    """Функция необходимая для внедрения зависимостей"""
    return
