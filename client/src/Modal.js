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
    currentPopulation, // 新增接收currentPopulation
    selectedIndices,   // 新增接收selectedIndices
    historicalSelections, 
    setSelectedIndices,
    onDeleteHistoricalRecord // 新增接收删除方法
  } = this.props;
  
  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>方案池</h2>
        
        {/* 当前代方案 */}
        <div className="current-generation">
          <h3>第{currentImages.generation}代选中方案</h3>
          <div className="modal-images">
            {Array.from(selectedIndices).map(index => ( // 直接使用selectedIndices
              <div key={`current-${index}`} className="modal-image-item">
                <img 
                  src={currentImages.images[index]} 
                  alt={`当前-${index}`}
                  className="modal-image"
                />
                <div className="vasecode">
                  {typeof currentPopulation?.[index=selectedIndices] === 'string' 
                    ? `${currentPopulation[index].substring(0, 10)}...` 
                    : '未知编码'}
                </div>
                <button 
                  className="delete-btn"
                  onClick={() => {
                    const newSet = new Set(selectedIndices);
                    newSet.delete(index);
                    setSelectedIndices(newSet);
                  }}
                >×</button>
              </div>
            ))}
          </div>
        </div>

        {/* 历史方案 */}
        <div className="historical-section">
          {historicalSelections.map((record, generationIndex) => (
            <div key={`gen-${generationIndex}`} className="generation-record">
              <h4>第{record.generation}代方案</h4>
              <div className="modal-images">
                {record.selections.map((item, idx) => (
                  <div key={`hist-${generationIndex}-${idx}`} className="modal-image-item">
                    <img 
                      src={item.base64} 
                      alt={`历史-${item.generation}-${item.selectedIndices}`}
                      className="modal-image"
                    />
                    <div className="vasecode">
                      {typeof item.vasecode === 'string' 
                        ? `${item.vasecode.substring(0, 10)}...` 
                        : '未知编码'}
                    </div>
                     <button 
                        className="delete-btn"
                        onClick={() => onDeleteHistoricalRecord(generationIndex, idx)}
                      >×</button>
                  </div>
                ))}
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