import React, { useState, useMemo } from 'react';

const SavingsCalculator = () => {
  const [activeTab, setActiveTab] = useState('future');
  
  // Tab 1: Tính tổng tiền sau thời gian
  const [futureInputs, setFutureInputs] = useState({
    principal: 100000000,
    periodicPayment: 1000000,
    years: 3.41,
    annualRate: 12,
    compoundFreq: 'monthly',
    interestType: 'compound' // 'simple' hoặc 'compound'
  });
  
  // Tab 2: Tính thời gian cần để đạt mục tiêu
  const [timeInputs, setTimeInputs] = useState({
    principal: 100000000,
    targetAmount: 200000000,
    periodicPayment: 1000000,
    annualRate: 12,
    compoundFreq: 'monthly',
    interestType: 'compound'
  });
  
  // Tab 3: Tính năng gấp đôi (đơn giản)
  const [doubleRate, setDoubleRate] = useState(12); // Lãi suất
  const [doubleYears, setDoubleYears] = useState(''); // Số năm (tự động tính)

  // Hàm tính FV với lãi kép (Compound Interest)
  const calculateCompoundFV = (pv, pmt, rate, nper, type = 1) => {
    if (rate === 0) return pv + pmt * nper;
    const pvFactor = pv * Math.pow(1 + rate, nper);
    const pmtFactor = pmt * ((Math.pow(1 + rate, nper) - 1) / rate) * (1 + rate * type);
    return pvFactor + pmtFactor;
  };

  // Hàm tính FV với lãi đơn (Simple Interest)
  const calculateSimpleFV = (pv, pmt, rate, nper) => {
    // Lãi đơn: FV = PV(1 + r*n) + PMT*n + PMT*r*n*(n+1)/2
    const pvWithInterest = pv * (1 + rate * nper);
    const totalPayments = pmt * nper;
    // Lãi trên các khoản gửi định kỳ (trung bình mỗi khoản sinh lãi trong n/2 kỳ)
    const paymentInterest = pmt * rate * nper * (nper + 1) / 2;
    return pvWithInterest + totalPayments + paymentInterest;
  };

  // Hàm tính NPER với lãi kép
  const calculateCompoundNPER = (rate, pmt, pv, fv, type = 1) => {
    if (rate === 0) return -(pv + fv) / pmt;
    const pmtAdj = pmt * (1 + rate * type);
    const num = Math.log((fv * rate + pmtAdj) / (pv * rate + pmtAdj));
    const den = Math.log(1 + rate);
    return num / den;
  };

  // Hàm tính NPER với lãi đơn (xấp xỉ bằng phương pháp Newton)
  const calculateSimpleNPER = (rate, pmt, pv, fv) => {
    // Phương trình: pv(1+r*n) + pmt*n + pmt*r*n*(n+1)/2 = fv
    // Giải bằng phương pháp Newton-Raphson
    let n = 1;
    for (let i = 0; i < 100; i++) {
      const f = pv * (1 + rate * n) + pmt * n + pmt * rate * n * (n + 1) / 2 - fv;
      const df = pv * rate + pmt + pmt * rate * (2 * n + 1) / 2;
      const nNew = n - f / df;
      if (Math.abs(nNew - n) < 0.0001) break;
      n = nNew;
    }
    return n;
  };

  // Tính toán cho Tab 1
  const futureResults = useMemo(() => {
    const { principal, periodicPayment, years, annualRate, compoundFreq, interestType } = futureInputs;
    
    let periodsPerYear, ratePerPeriod, totalPeriods, paymentPerPeriod;
    
    if (compoundFreq === 'monthly') {
      periodsPerYear = 12;
      ratePerPeriod = annualRate / 100 / 12;
      totalPeriods = years * 12;
      paymentPerPeriod = periodicPayment;
    } else if (compoundFreq === 'quarterly') {
      periodsPerYear = 4;
      ratePerPeriod = annualRate / 100 / 4;
      totalPeriods = years * 4;
      paymentPerPeriod = periodicPayment * 3;
    } else { // yearly
      periodsPerYear = 1;
      ratePerPeriod = annualRate / 100;
      totalPeriods = years;
      paymentPerPeriod = periodicPayment * 12;
    }
    
    const futureValue = interestType === 'compound' 
      ? calculateCompoundFV(principal, paymentPerPeriod, ratePerPeriod, totalPeriods)
      : calculateSimpleFV(principal, paymentPerPeriod, ratePerPeriod, totalPeriods);
    
    const totalDeposits = principal + paymentPerPeriod * totalPeriods;
    const interest = futureValue - totalDeposits;
    
    return {
      futureValue: Math.round(futureValue),
      interest: Math.round(interest),
      totalDeposits: Math.round(totalDeposits)
    };
  }, [futureInputs]);

  // Tính toán cho Tab 2
  const timeResults = useMemo(() => {
    const { principal, targetAmount, periodicPayment, annualRate, compoundFreq, interestType } = timeInputs;
    
    let ratePerPeriod, paymentPerPeriod, periodsPerYear;
    
    if (compoundFreq === 'monthly') {
      ratePerPeriod = annualRate / 100 / 12;
      paymentPerPeriod = periodicPayment;
      periodsPerYear = 12;
    } else if (compoundFreq === 'quarterly') {
      ratePerPeriod = annualRate / 100 / 4;
      paymentPerPeriod = periodicPayment * 3;
      periodsPerYear = 4;
    } else {
      ratePerPeriod = annualRate / 100;
      paymentPerPeriod = periodicPayment * 12;
      periodsPerYear = 1;
    }
    
    const periods = interestType === 'compound'
      ? calculateCompoundNPER(ratePerPeriod, -paymentPerPeriod, -principal, targetAmount)
      : calculateSimpleNPER(ratePerPeriod, paymentPerPeriod, principal, targetAmount);
    
    const years = periods / periodsPerYear;
    
    return {
      years: years,
      periods: periods
    };
  }, [timeInputs]);

  // Tính toán cho Tab 3 (Gấp đôi - đơn giản hóa)
  const doubleYearsCalc = useMemo(() => {
    if (!doubleRate || doubleRate <= 0) return '';
    const rate = doubleRate / 100;
    const years = Math.log(2) / Math.log(1 + rate);
    return years.toFixed(2);
  }, [doubleRate]);

  const doubleRateCalc = useMemo(() => {
    if (!doubleYears || doubleYears <= 0) return '';
    const rate = (Math.pow(2, 1 / parseFloat(doubleYears)) - 1) * 100;
    return rate.toFixed(2);
  }, [doubleYears]);

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('vi-VN').format(num) + ' ₫';
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 }).format(num);
  };

  const InputField = ({ label, value, onChange, type = "number", min, step, suffix }) => (
    <div className="input-group">
      <label>{label}</label>
      <div className="input-wrapper">
        <input
          type={type}
          value={value}
          onChange={onChange}
          min={min}
          step={step}
        />
        {suffix && <span className="suffix">{suffix}</span>}
      </div>
    </div>
  );

  const ResultCard = ({ label, value, highlight }) => (
    <div className={`result-card ${highlight ? 'highlight' : ''}`}>
      <div className="result-label">{label}</div>
      <div className="result-value">{value}</div>
    </div>
  );

  return (
    <div className="calculator-container">
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .calculator-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
          padding: 1rem;
          font-family: 'Arial', sans-serif;
        }

        .header {
          text-align: center;
          color: white;
          margin-bottom: 1.5rem;
        }

        .header h1 {
          font-size: 1.5rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          font-family: 'Georgia', serif;
        }

        .header p {
          font-size: 0.9rem;
          opacity: 0.9;
        }

        .main-card {
          max-width: 600px;
          margin: 0 auto;
          background: white;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
          overflow: hidden;
        }

        .tabs {
          display: flex;
          background: #f8f9fa;
          border-bottom: 2px solid #dee2e6;
        }

        .tab {
          flex: 1;
          padding: 1rem 0.5rem;
          background: none;
          border: none;
          font-size: 0.85rem;
          font-weight: 600;
          color: #495057;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
        }

        .tab.active {
          background: white;
          color: #1e3c72;
        }

        .tab.active::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          right: 0;
          height: 2px;
          background: #1e3c72;
        }

        .tab-content {
          padding: 1.5rem;
        }

        .section {
          margin-bottom: 1.5rem;
        }

        .section-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e3c72;
          margin-bottom: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 2px solid #1e3c72;
          font-family: 'Georgia', serif;
        }

        .input-group {
          margin-bottom: 1rem;
        }

        .input-group label {
          display: block;
          font-size: 0.9rem;
          font-weight: 600;
          color: #495057;
          margin-bottom: 0.5rem;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .input-wrapper input,
        .input-wrapper select {
          width: 100%;
          padding: 0.75rem 1rem;
          font-size: 1rem;
          border: 2px solid #ced4da;
          border-radius: 6px;
          transition: all 0.3s;
        }

        .input-wrapper input:focus,
        .input-wrapper select:focus {
          outline: none;
          border-color: #1e3c72;
          box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
        }

        .suffix {
          position: absolute;
          right: 1rem;
          color: #6c757d;
          font-weight: 600;
          pointer-events: none;
        }

        .radio-group {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .radio-option {
          flex: 1;
        }

        .radio-option input {
          display: none;
        }

        .radio-option label {
          display: block;
          padding: 0.75rem 0.5rem;
          border: 2px solid #ced4da;
          border-radius: 6px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s;
          font-weight: 600;
          font-size: 0.85rem;
        }

        .radio-option input:checked + label {
          background: #1e3c72;
          color: white;
          border-color: #1e3c72;
        }

        .results-grid {
          display: grid;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .result-card {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          border: 2px solid #dee2e6;
          text-align: center;
        }

        .result-card.highlight {
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white;
          border-color: #28a745;
        }

        .result-label {
          font-size: 0.85rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          opacity: 0.9;
        }

        .result-value {
          font-size: 1.3rem;
          font-weight: 700;
          font-family: 'Georgia', serif;
        }

        .info-text {
          background: #e7f3ff;
          border-left: 4px solid #0066cc;
          padding: 1rem;
          margin-top: 1rem;
          border-radius: 4px;
          font-size: 0.9rem;
          color: #004085;
          line-height: 1.5;
        }

        .double-container {
          display: grid;
          gap: 1rem;
        }

        .double-box {
          background: #f8f9fa;
          padding: 1.5rem;
          border-radius: 8px;
          border: 2px solid #dee2e6;
        }

        .double-box.highlight {
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white;
          border-color: #28a745;
        }

        .double-label {
          font-size: 0.9rem;
          font-weight: 600;
          margin-bottom: 0.75rem;
          opacity: 0.9;
        }

        .double-result {
          font-size: 2rem;
          font-weight: 700;
          font-family: 'Georgia', serif;
          margin-bottom: 0.5rem;
        }

        .double-caption {
          font-size: 0.85rem;
          opacity: 0.8;
        }

        .divider {
          text-align: center;
          margin: 1rem 0;
          color: #6c757d;
          font-weight: 600;
        }

        @media (min-width: 768px) {
          .calculator-container {
            padding: 2rem;
          }

          .header h1 {
            font-size: 2rem;
          }

          .tab {
            font-size: 1rem;
            padding: 1.25rem 1rem;
          }

          .tab-content {
            padding: 2rem;
          }
        }
      `}</style>

      <div className="header">
        <h1>Công Cụ Tính Toán Tiết Kiệm</h1>
        <p>Lập kế hoạch tài chính cho tương lai</p>
      </div>

      <div className="main-card">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'future' ? 'active' : ''}`}
            onClick={() => setActiveTab('future')}
          >
            Tính Tiền Tương Lai
          </button>
          <button 
            className={`tab ${activeTab === 'time' ? 'active' : ''}`}
            onClick={() => setActiveTab('time')}
          >
            Tính Thời Gian
          </button>
          <button 
            className={`tab ${activeTab === 'double' ? 'active' : ''}`}
            onClick={() => setActiveTab('double')}
          >
            Tính Gấp Đôi
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'future' && (
            <>
              <div className="section">
                <h3 className="section-title">Thông Tin Đầu Vào</h3>
                
                <div className="radio-group">
                  <div className="radio-option">
                    <input 
                      type="radio" 
                      id="compound" 
                      name="interestType"
                      checked={futureInputs.interestType === 'compound'}
                      onChange={() => setFutureInputs({...futureInputs, interestType: 'compound'})}
                    />
                    <label htmlFor="compound">Lãi kép</label>
                  </div>
                  <div className="radio-option">
                    <input 
                      type="radio" 
                      id="simple" 
                      name="interestType"
                      checked={futureInputs.interestType === 'simple'}
                      onChange={() => setFutureInputs({...futureInputs, interestType: 'simple'})}
                    />
                    <label htmlFor="simple">Lãi đơn</label>
                  </div>
                </div>
                
                <InputField
                  label="Số tiền hiện có"
                  value={futureInputs.principal}
                  onChange={(e) => setFutureInputs({...futureInputs, principal: Number(e.target.value)})}
                  step="1000000"
                  suffix="₫"
                />
                
                <InputField
                  label="Số tiền gửi mỗi tháng"
                  value={futureInputs.periodicPayment}
                  onChange={(e) => setFutureInputs({...futureInputs, periodicPayment: Number(e.target.value)})}
                  step="100000"
                  suffix="₫"
                />
                
                <InputField
                  label="Số năm tiết kiệm"
                  value={futureInputs.years}
                  onChange={(e) => setFutureInputs({...futureInputs, years: Number(e.target.value)})}
                  step="0.1"
                  suffix="năm"
                />
                
                <InputField
                  label="Lãi suất hàng năm"
                  value={futureInputs.annualRate}
                  onChange={(e) => setFutureInputs({...futureInputs, annualRate: Number(e.target.value)})}
                  step="0.1"
                  suffix="%"
                />
                
                <div className="input-group">
                  <label>Tần suất tính lãi</label>
                  <div className="input-wrapper">
                    <select 
                      value={futureInputs.compoundFreq}
                      onChange={(e) => setFutureInputs({...futureInputs, compoundFreq: e.target.value})}
                    >
                      <option value="monthly">Hàng tháng</option>
                      <option value="quarterly">Hàng quý</option>
                      <option value="yearly">Hàng năm</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="section">
                <h3 className="section-title">Kết Quả Dự Kiến</h3>
                
                <div className="results-grid">
                  <ResultCard 
                    label="Tổng tiền gửi"
                    value={formatCurrency(futureResults.totalDeposits)}
                  />
                  <ResultCard 
                    label="Tiền lãi"
                    value={formatCurrency(futureResults.interest)}
                  />
                  <ResultCard 
                    label="Tổng tiền cuối kỳ"
                    value={formatCurrency(futureResults.futureValue)}
                    highlight={true}
                  />
                </div>
              </div>
            </>
          )}

          {activeTab === 'time' && (
            <>
              <div className="section">
                <h3 className="section-title">Thông Tin Đầu Vào</h3>
                
                <div className="radio-group">
                  <div className="radio-option">
                    <input 
                      type="radio" 
                      id="compound2" 
                      name="interestType2"
                      checked={timeInputs.interestType === 'compound'}
                      onChange={() => setTimeInputs({...timeInputs, interestType: 'compound'})}
                    />
                    <label htmlFor="compound2">Lãi kép</label>
                  </div>
                  <div className="radio-option">
                    <input 
                      type="radio" 
                      id="simple2" 
                      name="interestType2"
                      checked={timeInputs.interestType === 'simple'}
                      onChange={() => setTimeInputs({...timeInputs, interestType: 'simple'})}
                    />
                    <label htmlFor="simple2">Lãi đơn</label>
                  </div>
                </div>
                
                <InputField
                  label="Số tiền hiện có"
                  value={timeInputs.principal}
                  onChange={(e) => setTimeInputs({...timeInputs, principal: Number(e.target.value)})}
                  step="1000000"
                  suffix="₫"
                />
                
                <InputField
                  label="Số tiền mục tiêu"
                  value={timeInputs.targetAmount}
                  onChange={(e) => setTimeInputs({...timeInputs, targetAmount: Number(e.target.value)})}
                  step="1000000"
                  suffix="₫"
                />
                
                <InputField
                  label="Số tiền gửi mỗi tháng"
                  value={timeInputs.periodicPayment}
                  onChange={(e) => setTimeInputs({...timeInputs, periodicPayment: Number(e.target.value)})}
                  step="100000"
                  suffix="₫"
                />
                
                <InputField
                  label="Lãi suất hàng năm"
                  value={timeInputs.annualRate}
                  onChange={(e) => setTimeInputs({...timeInputs, annualRate: Number(e.target.value)})}
                  step="0.1"
                  suffix="%"
                />
                
                <div className="input-group">
                  <label>Tần suất tính lãi</label>
                  <div className="input-wrapper">
                    <select 
                      value={timeInputs.compoundFreq}
                      onChange={(e) => setTimeInputs({...timeInputs, compoundFreq: e.target.value})}
                    >
                      <option value="monthly">Hàng tháng</option>
                      <option value="quarterly">Hàng quý</option>
                      <option value="yearly">Hàng năm</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="section">
                <h3 className="section-title">Kết Quả Tính Toán</h3>
                
                <div className="results-grid">
                  <ResultCard 
                    label="Thời gian cần thiết"
                    value={`${formatNumber(timeResults.years)} năm`}
                    highlight={true}
                  />
                  <ResultCard 
                    label={`Số kỳ ${timeInputs.compoundFreq === 'monthly' ? 'tháng' : timeInputs.compoundFreq === 'quarterly' ? 'quý' : 'năm'}`}
                    value={formatNumber(timeResults.periods)}
                  />
                </div>

                <div className="info-text">
                  Với số tiền hiện có <strong>{formatCurrency(timeInputs.principal)}</strong> và gửi thêm <strong>{formatCurrency(timeInputs.periodicPayment)}/tháng</strong>, bạn sẽ đạt <strong>{formatCurrency(timeInputs.targetAmount)}</strong> sau <strong>{Math.floor(timeResults.years)} năm {Math.round((timeResults.years % 1) * 12)} tháng</strong>.
                </div>
              </div>
            </>
          )}

          {activeTab === 'double' && (
            <div className="section">
              <h3 className="section-title">Kế Quả Tính Toán</h3>
              
              <div className="double-container">
                <div className="double-box">
                  <div className="double-label">Điền lãi suất (%/năm)</div>
                  <input
                    type="number"
                    value={doubleRate}
                    onChange={(e) => setDoubleRate(e.target.value)}
                    step="0.1"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      fontSize: '1rem',
                      border: '2px solid #ced4da',
                      borderRadius: '6px',
                      marginBottom: '1rem'
                    }}
                  />
                  {doubleYearsCalc && (
                    <>
                      <div className="double-result">{doubleYearsCalc}</div>
                      <div className="double-caption">năm để gấp đôi</div>
                    </>
                  )}
                </div>

                <div className="divider">HOẶC</div>

                <div className="double-box">
                  <div className="double-label">Điền số năm</div>
                  <input
                    type="number"
                    value={doubleYears}
                    onChange={(e) => setDoubleYears(e.target.value)}
                    step="0.1"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      fontSize: '1rem',
                      border: '2px solid #ced4da',
                      borderRadius: '6px',
                      marginBottom: '1rem'
                    }}
                  />
                  {doubleRateCalc && (
                    <>
                      <div className="double-result">{doubleRateCalc}%</div>
                      <div className="double-caption">lãi suất/năm cần thiết</div>
                    </>
                  )}
                </div>
              </div>

              <div className="info-text" style={{marginTop: '1.5rem'}}>
                <strong>Quy tắc 72:</strong> Ước tính nhanh bằng cách chia 72 cho lãi suất (%). 
                Ví dụ: Lãi suất 12% → 72 ÷ 12 = 6 năm để gấp đôi.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SavingsCalculator;