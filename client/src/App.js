import './App.css';
import React, { useState, useEffect, useRef } from 'react';
import webgazer from 'webgazer';
import Modal from './Modal';

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
  
  const [isModalOpen, setIsModalOpen] = useState(false); // 新增弹窗
  const [historicalSelections, setHistoricalSelections] = useState([]); // 新增历史精英选择。

  const [initializeClickCount, setInitializeClickCount] = useState(0); // 新增：记录初始化按钮点击次数
  // A版
  // 新增初始化 ratings 状态，确保长度为16，初始值为1
  const [ratings, setRatings] = useState(Array(16).fill(1)); // 修改此处


  // 新增 handleRatingChange 函数
  const handleRatingChange = (index, value) => {
    const newRatings = [...ratings];
    newRatings[index] = value;
    setRatings(newRatings);
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
        
        //保存历史记录
        const currentGeneration = historicalSelections.length + 1;
        const selectedItems = Array.from(selectedIndices).map(index => ({
          vasecode: currentPopulation[index], // 假设currentPopulation存储的是vasecode
          base64: jpgUrls[index],
          generation: currentGeneration,
          index: index,
      

        }));

        console.log('保存的历史记录:', selectedItems); // 调试日志

        setHistoricalSelections(prev => [...prev, {
          generation: currentGeneration,
          selections: selectedItems
        }]);


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
            <h2>请确保你已评分，且已选择0-3个方案</h2>
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
          {isEvolving ? '运行中...' : '实验开始'}
        </button>

        {/*<button onClick={handleEvolve}>方案迭代 Evolve</button>*/}
        <button
          onClick={handleEvolve}
          disabled={isEvolving}  // 绑定防抖状态
        >
          {isEvolving ? '运行中...' : '方案迭代'}
        </button>

         <button
          onClick={() => setIsModalOpen(true)}
          // disabled={selectedIndices.size === 0}
        >
          查看购物车
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
            
            {/* 弹窗 */}
            <Modal
              isOpen={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              images={svgImages}
                currentImages={{
                images: svgImages,
                selectedIndices,
                generation: historicalSelections.length + 1
              }}
              currentPopulation={currentPopulation} // 新增传递当前种群
              selectedIndices={selectedIndices} // 新增传递选中索引
              historicalSelections={historicalSelections}
              setSelectedIndices={setSelectedIndices}
              
              // 新增：添加删除历史记录的方法
              onDeleteHistoricalRecord={(generationIndex, recordIndex) => {
                const newHistorical = [...historicalSelections];
                newHistorical[generationIndex].selections.splice(recordIndex, 1);
                if (newHistorical[generationIndex].selections.length === 0) {
                  newHistorical.splice(generationIndex, 1);
                }
                setHistoricalSelections(newHistorical);
              }}
            />

            

            {/* 滑动条在图片容器底部 */}
            <div className="rating-wrapper">
              <div className="rating-container">
                <span></span>
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

                  {/* 新增显示数值的小方块 */}
                  <div className="rating-value">{ratings[index]}</div> 
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

