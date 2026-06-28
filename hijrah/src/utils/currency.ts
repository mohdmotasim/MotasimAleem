export const formatCurrency = (
  amount: number,
  currency: 'USD' | 'INR' | 'LOCAL',
  exchangeRateUSDToINR: number = 83.5,
  localCurrencySymbol: string = '$'
): string => {
  let convertedAmount = amount;
  let symbol = '$';

  switch (currency) {
    case 'USD':
      convertedAmount = amount;
      symbol = '$';
      break;
    case 'INR':
      convertedAmount = amount * exchangeRateUSDToINR;
      symbol = '₹';
      break;
    case 'LOCAL':
      convertedAmount = amount;
      symbol = localCurrencySymbol;
      break;
  }

  return `${symbol}${convertedAmount.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`;
};

export const convertCurrency = (
  amount: number,
  from: 'USD' | 'INR',
  to: 'USD' | 'INR',
  exchangeRateUSDToINR: number = 83.5
): number => {
  if (from === to) return amount;
  
  if (from === 'USD' && to === 'INR') {
    return amount * exchangeRateUSDToINR;
  }
  
  if (from === 'INR' && to === 'USD') {
    return amount / exchangeRateUSDToINR;
  }
  
  return amount;
};
