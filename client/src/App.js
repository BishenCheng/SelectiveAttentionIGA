import './App.css';
import React, { useState, useEffect, useRef } from 'react';
import webgazer from 'webgazer';

function App() {
  const [svgImages, setSvgImages] = useState(Array(16).fill(null));
  const [gazeTimes, setGazeTimes] = useState(Array(16).fill(0));
  const [selectedIndices, setSelectedIndices] = useState(new Set()); // 记录选中的容器索引
  const [gazeRecords, setGazeRecords] = useState([]); // 存储注视路径记录
  const containerRefs = useRef(Array(16).fill().map(() => React.createRef()));
  const startTimeRefs = useRef(Array(16).fill(null));
  const [webgazerError, setWebgazerError] = useState(null);
  const [elitePositions, setElitePositions] = useState([]); // 存储精英位置
  const isWebgazerInitialized = useRef(false);
  const [currentPopulation, setCurrentPopulation] = useState([]);
  const prevContainerIndexRef = useRef(null); // 记录上一个注视的容器索引

  const [isEvolving, setIsEvolving] = useState(false); // 防止重复点击迭代按钮
  const [isInitializing, setIsInitializing] = useState(false); // 防止重复点击初始化按钮

  const [experimentEnded, setExperimentEnded] = useState(false); // 新增：实验是否已完成
  const[EchoMessage,setEchoMessage] = useState(false);//新增：提醒用户去浏览选择

  const [initializeClickCount, setInitializeClickCount] = useState(0); // 新增：记录初始化按钮点击次数
  // A版
  // 新增初始化 ratings 状态，确保长度为16，初始值为3
  const [ratings, setRatings] = useState(Array(16).fill(3)); // 修改此处


  // 加载indexDB 跨域通信机制。接听3001端口的消息。
  const [dbdata, setData] = useState(null);
  const [writeStatus, setWriteStatus] = useState('');

  // 新增 handleRatingChange 函数
  const handleRatingChange = (index, value) => {
    const newRatings = [...ratings];
    newRatings[index] = value;
    setRatings(newRatings);
  };

  // 打开 3001 页面并发送请求
  const handleGetDataAndWrite = () => {
    if (!window.otherWindow || window.otherWindow.closed) {
      window.otherWindow = window.open('http://localhost:3001/calibration.html?', '_blank');
    }

    window.otherWindow.postMessage(
      { type: 'read', key: 'webgazerGlobalData' },
      'http://localhost:3001/calibration.html?'
    );
  };

  // 接收 3001 返回的数据并写入本地 IndexedDB
  useEffect(() => {
    const handleMessage = async (event) => {
      if (event.origin !== 'http://localhost:3001/calibration.html?') return;

      if (event.data && event.data.type === 'response') {
        const dbdata = event.data.data;

        try {
          // 写入到 3000 的 IndexedDB
          await writeDataToIndexedDB(dbdata);
          setWriteStatus('数据写入成功');
        } catch (error) {
          setWriteStatus('写入失败:' + error.message);
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
    console.log('开始写入数据:', dbdata); // 添加日志
    const request = indexedDB.open('localforge', 1); // 数据库名称和版本
    return new Promise((resolve, reject) => {
      request.onerror = (event) => {
        console.error('打开数据库失败:', event.target.error); // 明确输出错误
        reject('打开数据库失败:', event.target.error);
      };

      request.onsuccess = (event) => {
        const db = event.target.result;
        console.log('数据库已打开:', db); // 确认数据库打开成功

        const transaction = db.transaction(['keyvaluepairs'], 'readwrite');
        const store = transaction.objectStore('keyvaluepairs');

        // 使用 put 方法更新或插入数据
        const putRequest = store.put(dbdata, 'webgazerGlobalData'); // key 为 "webgazerGlobalData"

        putRequest.onsuccess = () => {
          db.close();
          console.log('写入成功'); // 确认写入成功
          resolve('数据已写入');
        };

        putRequest.onerror = (event) => {
          console.error('写入失败:', event.target.error); // 明确输出错误
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

  // 加载 webgazer.js 设置监听器.（本地脚本版本）
  // useEffect(() => {

  //   if (window.__gazeListenerAttached) return;
  //   window.__gazeListenerAttached = true;

  //   if (isWebgazerInitialized.current) return;

  //   const script = document.createElement('script');
  //   script.src = '/webgazer.js';
  //   script.async = true;
  //   script.onerror = () => {
  //     setWebgazerError("Failed to load webgazer.js. 请检查 public 目录下是否存在该文件");
  //   };

  //   script.onload = () => {
  //     window.webgazer
  //       .begin()
  //       .then(api => {
  //         console.log('WebGazer 初始化成功');

  //         // 注视点监听
  //         api.setGazeListener((data, clock) => {
  //           if (!data) return;
  //           const x = data.x;
  //           const y = data.y;

  //           containerRefs.current.forEach((ref, index) => {
  //             const container = ref.current;
  //             if (!container) return;

  //             const rect = container.getBoundingClientRect();
  //             const isInside = x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;

  //             // 进入容器
  //             if (isInside && !startTimeRefs.current[index]) {
  //               startTimeRefs.current[index] = Date.now();

  //               // 首次注视处理逻辑:构建自指边
  //               if (prevContainerIndexRef.current === null) {
  //                 // 生成自指记录
  //                 const record = {
  //                   timestamp: new Date().toISOString(),
  //                   source_container: index,
  //                   target_container: index,
  //                   duration_weight: 0,  // 初始值设为0，离开时更新
  //                   is_selected: selectedIndices.has(index)
  //                 };
  //                 setGazeRecords(prev => [...prev, record]);
  //               }
  //               // 记录上一个容器到当前容器的转移
  //               else if (prevContainerIndexRef.current !== index) {
  //                 const prevIndex = prevContainerIndexRef.current;
  //                 const record = {
  //                   timestamp: new Date().toISOString(),
  //                   source_container: prevIndex,
  //                   target_container: index,
  //                   duration_weight: 0,  // 初始值设为0，离开时更新
  //                   is_selected: selectedIndices.has(index)
  //                 };
  //                 setGazeRecords(prev => [...prev, record]);
  //               }
  //               prevContainerIndexRef.current = index;
  //             }

  //             // 离开容器
  //             if (!isInside && startTimeRefs.current[index]) {
  //               const duration = (Date.now() - startTimeRefs.current[index]) ;  // 转换为秒

  //               // 更新最后一条记录的duration
  //               setGazeRecords(prevRecords => {
  //                 if (prevRecords.length === 0) return prevRecords;

  //                 const lastRecord = { ...prevRecords[prevRecords.length - 1] };
  //                 if (lastRecord.target_container === index) {
  //                   lastRecord.duration_weight = duration;
  //                   return [
  //                     ...prevRecords.slice(0, prevRecords.length - 1),
  //                     lastRecord
  //                   ];
  //                 }

  //                 return prevRecords;
  //               });

  //               // 更新注视时间
  //               setGazeTimes(prev => {
  //                 const newTimes = [...prev];
  //                 newTimes[index] += duration;
  //                 return newTimes;
  //               });

  //               startTimeRefs.current[index] = null;
  //             }
  //           });
  //         });

  //         api.showPredictionPoints(false);
  //         isWebgazerInitialized.current = true;
  //       })
  //       .catch(err => {
  //         console.error("WebGazer 初始化失败:", err);
  //         setWebgazerError(`WebGazer 初始化失败: ${err.message}`);
  //       });

  //     return () => {
  //       window.webgazer.end();
  //       window.__gazeListenerAttached = false;
  //     };
  //   };
  //   document.body.appendChild(script);
  // }, []);

  
  // 加载 webgazer.js 设置监听器.
  useEffect(() => {

    if (window.__gazeListenerAttached) return;
    window.__gazeListenerAttached = true;

    if (isWebgazerInitialized.current) return;

    // 如果是 npm 安装并使用 import 引入 webgazer，则可以直接调用 begin()。
    webgazer
      .begin()
      .then(api => {
        console.log('WebGazer 初始化成功');

        // 注视点监听
        api.setGazeListener((data, clock) => {
          if (!data) return;
          const x = data.x;
          const y = data.y;

          containerRefs.current.forEach((ref, index) => {
            const container = ref.current;
            if (!container) return;

            const rect = container.getBoundingClientRect();
            const isInside = x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;

            // 进入容器
            if (isInside && !startTimeRefs.current[index]) {
              startTimeRefs.current[index] = Date.now();

              // 首次注视处理逻辑:构建自指边
              if (prevContainerIndexRef.current === null) {
                // 生成自指记录
                const record = {
                  timestamp: new Date().toISOString(),
                  source_container: index,
                  target_container: index,
                  duration_weight: 0,  // 初始值设为0，离开时更新
                  is_selected: selectedIndices.has(index)
                };
                setGazeRecords(prev => [...prev, record]);
              }
              // 记录上一个容器到当前容器的转移
              else if (prevContainerIndexRef.current !== index) {
                const prevIndex = prevContainerIndexRef.current;
                const record = {
                  timestamp: new Date().toISOString(),
                  source_container: prevIndex,
                  target_container: index,
                  duration_weight: 0,  // 初始值设为0，离开时更新
                  is_selected: selectedIndices.has(index)
                };
                setGazeRecords(prev => [...prev, record]);
              }
              prevContainerIndexRef.current = index;
            }

            // 离开容器
            if (!isInside && startTimeRefs.current[index]) {
              const duration = (Date.now() - startTimeRefs.current[index]);  // 转换为毫秒

              // 更新最后一条记录的duration
              setGazeRecords(prevRecords => {
                if (prevRecords.length === 0) return prevRecords;

                const lastRecord = { ...prevRecords[prevRecords.length - 1] };
                if (lastRecord.target_container === index) {
                  lastRecord.duration_weight = duration;
                  return [
                    ...prevRecords.slice(0, prevRecords.length - 1),
                    lastRecord
                  ];
                }

                return prevRecords;
              });

              // 更新注视时间
              setGazeTimes(prev => {
                const newTimes = [...prev];
                newTimes[index] += duration;
                return newTimes;
              });

              startTimeRefs.current[index] = null;
            }
          });
        });

        api.showPredictionPoints(false);
        isWebgazerInitialized.current = true;
      })
      .catch(err => {
        console.error("WebGazer 初始化失败:", err);
        setWebgazerError(`WebGazer 初始化失败: ${err.message}`);
      });

    return () => {
      // window.webgazer.end();
      // window.__gazeListenerAttached = false;
      if (window.webgazer && typeof window.webgazer.end === 'function') {
        try {
          window.webgazer.end();
        } catch (e) {
          console.warn('Webgazer cleanup warning:', e);
        }
      }
      window.__gazeListenerAttached = false;
      isWebgazerInitialized.current = false;
    };

  }, []);


  const handleContainerClick = (index) => {

    // 使用函数式更新确保获取最新状态
    setSelectedIndices(prev => {
      const newSelected = new Set(prev); // 基于最新状态创建新Set
      if (newSelected.has(index)) {
        newSelected.delete(index);
      } else {
        newSelected.add(index);
      }

      // 如果选中数量超过3个，则移除最早选中的项
      if (newSelected.size > 3) {
        const firstIndex = [...newSelected][0]; // 获取最早选中的索引
        newSelected.delete(firstIndex);
      }
      return newSelected; // 返回新的Set实例触发重渲染
    });
  };

  const handleInitialize = async () => {
    if (experimentEnded || initializeClickCount >= 2) return; // 如果已经点击过两次或实验结束，则不再响应

    setIsInitializing(true); // 开启防抖锁
    setInitializeClickCount(prev => prev + 1); // 更新点击次数

    // 初始化时清空记录
    setGazeRecords([]);
    setSelectedIndices(new Set());
    try {
      const response = await fetch('http://localhost:8000/initialize/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          num_genes: 32,
          population_size: 16,
        }),
      });
      if (!response.ok) {
        throw new Error(`初始化请求失败，状态码: ${response.status}`);
      }

      const data = await response.json();
      console.log('初始化响应数据:', data);
      if (data.jpg_base64 && data.population) {
        // const svgUrls = data.svg.map((base64Svg) => {
        //   try {
        //     const decodedSvg = atob(base64Svg);
        //     const modifiedSvg = decodedSvg.replace(/<svg/, '<svg class="image-item"');
        //     const blob = new Blob([modifiedSvg], { type: 'image/svg+xml' });
        //     return URL.createObjectURL(blob);
        //   } catch (error) {
        //     console.error('创建 SVG URL 失败:', error);
        //     return null;
        //   }
        // });
        const jpgUrls = data.jpg_base64.map(base64Jpg => `data:image/png;base64,${base64Jpg}`);
        setSvgImages(jpgUrls);
        setCurrentPopulation(data.population);
        setRatings(Array(16).fill(0));//初始化评分为0
      } else {
        console.error('响应数据中缺少必要字段');
      }
    } catch (error) {
      console.error('初始化失败:', error);
    }finally {
      setIsInitializing(false); // 释放防抖锁
    }
  };

  const handleEvolve = async () => {

    // 调试信息
    console.log('--- 迭代开始前的数据 ---');
    console.log('currentPopulation:', currentPopulation);
    console.log('selectedIndices:', Array.from(selectedIndices));
    console.log('gazeRecords:', gazeRecords);
    console.log('prevContainerIndexRef:', prevContainerIndexRef.current);

    // 确保选中索引不超过3个，否则移除最早选中的
    let limitedSelectedIndices = [...selectedIndices];
    if (limitedSelectedIndices.length > 3) {
      limitedSelectedIndices.shift(); // 删除第一个元素
    }

    if (isEvolving) return; // 防止重复调用

    setIsEvolving(true); // 开启防抖锁
    try {
      // 整理最终选中状态到记录（最后一次选中）
      const finalRecords = gazeRecords.map(record => ({
        ...record,
        is_selected: selectedIndices.has(record.target_container)
      }));

      const response = await fetch('http://localhost:8000/evolve/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          population: currentPopulation,
          gaze_records: finalRecords, // 传递注视记录
          selected_indices: Array.from(selectedIndices), // 传递选中索引
          ratings: ratings.map(r => r || 0) // 默认0防止undefined
        }),
      });
      if (!response.ok) {
        throw new Error(`迭代请求失败，状态码: ${response.status}`);
      }
      const data = await response.json();
      console.log('迭代响应数据:', data);
      if (data.new_jpg && data.new_population) {
        const jpgUrls = data.new_jpg.map(base64Jpg => `data:image/png;base64,${base64Jpg}`);

        setSvgImages(jpgUrls);
        setGazeRecords([]); // 清空注视记录
        prevContainerIndexRef.current = null; // 重置注视容器索引
        setRatings(Array(16).fill(0));//归0
        setGazeTimes(Array(16).fill(0)); // 重置注视时间
        setCurrentPopulation(data.new_population);
        setElitePositions(data.elite_positions || []); // 保存精英位置
        setSelectedIndices(new Set()); // 清空选中项

        setExperimentEnded(false); // 实验未结束
        setEchoMessage(false); // 无需提示

      } else {
        console.error('响应数据中缺少必要字段');
        setExperimentEnded(true); // 数据异常也标记为结束
        // setEchoMessage(true);// 数据异常标记
      }
    } catch (error) {
      console.error('迭代失败:', error);
      //setExperimentEnded(true); // 出错时也标记为结束
      setEchoMessage(true);// 数据异常标记

    } finally {
      setIsEvolving(false); // 释放防抖锁
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
      <h1>智能设计实验平台</h1>
      {webgazerError && <p className="error-message">**Error:** {webgazerError}</p>}

      {/* 实验结束提示 */}
      {experimentEnded && (
          <div className="experiment-ended-message">
            <h2>实验结束，感谢你的参与</h2>
          </div>
      )}
      {EchoMessage && (
          <div className="experiment-echo-message">
            <h2>请确保你已浏览，且已选择1-3个方案</h2>
          </div>
      )}

      {/*<div className="control-buttons">*/}
      {/*  <button onClick={handleGetDataAndWrite}>获取并写入 3001 数据</button>*/}
      {/*  {writeStatus && <p>{writeStatus}</p>}*/}
      {/*</div>*/}
      
      <div className="control-buttons">

        <button
            onClick={handleInitialize}
            disabled={initializeClickCount >= 2 || isInitializing} // 点击两次后禁用按钮
        >
          {isEvolving ? '运行中...' : '开始 Intialize'}
        </button>

        {/*<button onClick={handleEvolve}>方案迭代 Evolve</button>*/}
        <button
          onClick={handleEvolve}
          disabled={isEvolving}  // 绑定防抖状态
        >
          {isEvolving ? '运行中...' : '方案迭代   Evolve'}
        </button>
    
      </div>
      </div>

      <div className="main-content">

        <div className="images-container">
        {svgImages.map((imageUrl, index) => (
          <div 
            key={index}
            className="image-item-container"  // 新增统一容器类名
          >
            <div
              className={`image-item ${selectedIndices.has(index) ? 'selected' : ''} ${elitePositions.includes(index) ? 'elite' : ''}`}
              ref={containerRefs.current[index]}
              onClick={() => handleContainerClick(index)}
            >
              <div className="content-wrapper">
                {imageUrl && (
                    <img
                        src={imageUrl}
                        alt={`Vase ${index}`}
                        className="image-content"
                        style={{ pointerEvents: 'none' }}
                    />
                )}
              </div>
            </div>
            
            {/* 滑动条在图片容器底部 */}
            <div className="rating-wrapper">
              <div className="rating-container">
                <span>1</span>
                <input 
                  type="range" 
                  min="1" 
                  max="5" 
                  value={ratings[index] || 0} 
                  onChange={(e) => handleRatingChange(index, parseInt(e.target.value))}
                  onClick={(e) => e.stopPropagation()}
                  //className="rating-slider"
                  className={`rating-slider ${ratings[index] > 0 ? 'green-slider' : ''}`}
                />
                <span>5</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      

      
      
      </div>
    </div>
  );
}

export default App;

