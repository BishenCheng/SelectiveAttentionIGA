const [dbdata, setData] = useState(null);
const [writeStatus, setWriteStatus] = useState('');

  // 打开 3001 页面并发送请求
  const handleGetDataAndWrite = () => {
    if (!window.otherWindow || window.otherWindow.closed) {
      window.otherWindow = window.open('http://localhost:3001', '_blank');
    }

    window.otherWindow.postMessage(
      { type: 'read', key: 'webgazerGlobalData' },
      'http://localhost:3001'
    );
  };

  // 接收 3001 返回的数据并写入本地 IndexedDB
  useEffect(() => {
    const handleMessage = async (event) => {
      if (event.origin !== 'http://localhost:3001') return;

      if (event.dbdata.type === 'response') {
        const receivedData = event.dbdata.data;

        try {
          // 写入到 3000 的 IndexedDB
          await writeDataToIndexedDB(receivedData);
          setWriteStatus('✅ 数据写入成功');
        } catch (error) {
          setWriteStatus('❌ 写入失败: ' + error.message);
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  // 写入 IndexedDB 的函数
  const writeDataToIndexedDB = async (dbdata) => {
    const request = indexedDB.open('localforge', 1); // 数据库名称和版本
    return new Promise((resolve, reject) => {
      request.onerror = (event) => {
        reject('打开数据库失败:', event.target.error);
      };

      request.onsuccess = (event) => {
        const db = event.target.result;

        const transaction = db.transaction(['keyvaluepairs'], 'readwrite');
        const store = transaction.objectStore('keyvaluepairs');

        // 使用 put 方法更新或插入数据
        const putRequest = store.put(dbdata, 'webgazerGlobalData'); // key 为 "webgazerGlobalData"

        putRequest.onsuccess = () => {
          db.close();
          resolve('数据已写入');
        };

        putRequest.onerror = (event) => {
          db.close();
          reject('写入失败:', event.target.error);
        };
      };

      // 如果数据库不存在或需要升级
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('keyvaluepairs')) {
          db.createObjectStore('keyvaluepairs', { keyPath: 'id' }); // 根据你的结构调整 keyPath
        }
      };
    });
  };