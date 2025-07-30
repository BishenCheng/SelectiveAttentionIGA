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

  // 渲染机制
    render() {
    const { 
      isOpen, 
      onClose, 
      currentImages, 
      currentPopulation, 
      selectedIndices,   
      historicalSelections, 
      setSelectedIndices,
      onDeleteHistoricalRecord,
      modalError, 
      onLogOperation 
    } = this.props;
    
    if (!isOpen) return null;

    const formatVaseCode = (vasecode) => {
      if (Array.isArray(vasecode)) {
        return vasecode.join(', ').substring(0, 30) + '...';
      }
      return typeof vasecode === 'string' ? `${vasecode.substring(0, 30)}...` : '在当前批次';
    };

    // 合并当前代和历史方案，但保持固定位置
    const allItems = [];
    
    // 添加当前代的方案
    Array.from({length: currentPopulation.length}, (_, idx) => idx)
      .filter(index => selectedIndices.has(index))
      .forEach(index => {
        allItems.push({
          ...currentPopulation[index],
          base64: currentImages.images[index],
          generation: currentImages.generation,
          index,
          type: 'current',
          key: `current-${currentImages.generation}-${index}`
        });
      });

    // 添加历史代的方案
    historicalSelections.forEach(record => {
      record.selections.forEach((selection, idx) => {
        allItems.push({
          ...selection,
          type: 'historical',
          recordGeneration: record.generation,
          recordIndex: historicalSelections.findIndex(r => r.generation === record.generation),
          itemIndex: idx,
          key: `historical-${record.generation}-${idx}`
        });
      });
    });

    return ReactDOM.createPortal(
      <div className="modal-overlay">
        <div className="modal-content">
          <button className="close-btn" onClick={onClose}>×</button>
          <h1>方案池</h1>
          {modalError && <p className="modal-error" style={{ color: 'red', margin: '10px 0' }}>{modalError}</p>} 
          <p>点击方案的右上角x图标可以删除该方案，点击右上角退出方案池</p>
          
          {/* 统一显示所有方案 */}
          <div className="all-modal-images">
            {allItems.map((item, index) => {
              if (!item) {
                console.warn(`Item at index ${index} is undefined`);
                return null;
              }
              return (
                <div key={item.key} className="modal-image-item">
                  <img 
                    src={item.base64} 
                    alt={`方案-${item.generation || item.recordGeneration}-${item.index || index}`}
                    className="modal-image"
                  />
                  {/* 新增批次号显示 */}
                  <div className="generation-number">方案批次: {item.generation || item.recordGeneration}</div>
                  <div className="vasecode">
                    {formatVaseCode(item.vasecode)}
                  </div>
                  <button 
                    className="delete-btn"
                    onClick={() => {
                      if (item.type === 'current') {
                        // 删除当前代的方案
                        const newSet = new Set(selectedIndices);
                        newSet.delete(item.index);
                        setSelectedIndices(newSet);
                      } else {
                        // 删除历史代的方案
                        onDeleteHistoricalRecord(item.recordIndex, item.itemIndex);
                      }
                      onLogOperation(item.generation || item.recordGeneration, item.vasecode, 'remove');
                    }}
                  >x</button>
                </div>
              );
            })}
          </div>
        </div>
      </div>,
      this.el
    );
  }
}

export default Modal;