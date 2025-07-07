import React from 'react';
import ReactDOM from 'react-dom';

const modalRoot = document.getElementById('modal-root');

class Modal extends React.Component {
  constructor(props) {
    super(props);
    this.el = document.createElement('div');
  }

  componentDidMount() {
    modalRoot.appendChild(this.el);
  }

  componentWillUnmount() {
    modalRoot.removeChild(this.el);
  }

  render() {
    const { 
      isOpen, 
      onClose, 
      currentImages, 
      currentPopulation, 
      selectedIndices,   
      historicalSelections, 
      setSelectedIndices,
      onDeleteHistoricalRecord 
    } = this.props;
    
    if (!isOpen) return null;

    // 辅助函数，将 vasecode 列表转换为字符串
    const formatVaseCode = (vasecode) => {
      if (Array.isArray(vasecode)) {
        return vasecode.join(', ').substring(0, 30) + '...';
      }
      return typeof vasecode === 'string' ? `${vasecode.substring(0, 30)}...` : '未知编码';
    };

    return ReactDOM.createPortal(
      <div className="modal-overlay">
        <div className="modal-content">
          <button className="close-btn" onClick={onClose}>×</button>
          <h2>方案池</h2>
          <p>点击右上角退出</p>
          
          {/* 当前代方案 */}
          <div className="current-generation">
            <h3>第{currentImages.generation}代选中方案</h3>
            <div className="modal-images">
              {Array.from({length: currentPopulation.length}, (_, idx) => idx)
                .filter(index => selectedIndices.has(index))
                .map(index => {
                  const item = currentPopulation[index]; 
                  if (!item) {
                    console.warn(`Item at index ${index} is undefined`);
                    return null;
                  }
                  return (
                    <div key={`current-${index}`} className="modal-image-item">
                      <img 
                        src={currentImages.images[index]} 
                        alt={`当前-${index}`}
                        className="modal-image"
                      />
                      <div className="vasecode">
                        {/* 使用辅助函数格式化 vasecode */}
                        {formatVaseCode(item.vasecode)}
                      </div>
                      
                      <button 
                        className="delete-btn"
                        onClick={() => {
                          const newSet = new Set(selectedIndices);
                          newSet.delete(index);
                          setSelectedIndices(newSet);
                        }}
                      >x</button>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* 历史方案 */}
          <div className="historical-section">
            {historicalSelections.map((record, generationIndex) => (
              <div key={`gen-${generationIndex}`} className="generation-record">
                <h4>第{record.generation}代方案</h4>
                <div className="modal-images">
                  {record.selections.map((item, idx) => {
                    if (!item) {
                      console.warn(`Historical item at generation ${generationIndex}, index ${idx} is undefined`);
                      return null;
                    }

                    return ( 
                      <div key={`hist-${generationIndex}-${idx}`} className="modal-image-item">
                        <img 
                          src={item.base64} 
                          alt={`历史-${item.generation}-${item.selectedIndices}`}
                          className="modal-image"
                        />
                        <div className="vasecode">
                          {/* 使用辅助函数格式化 vasecode */}
                          {formatVaseCode(item.vasecode)}
                        </div>
                        <button 
                          className="delete-btn"
                          onClick={() => onDeleteHistoricalRecord(generationIndex, idx)}
                        >x</button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>


        </div>
      </div>,
      this.el
    );
  }
}

export default Modal;