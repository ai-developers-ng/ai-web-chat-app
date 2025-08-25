const express = require('express');
const router = express.Router();
const Product = require('../models/Product');

// Track affiliate link click
router.post('/click/:productId', async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(
      req.params.productId,
      { $inc: { clickCount: 1 } },
      { new: true }
    );
    if (!product) return res.status(404).json({ message: 'Product not found' });
    res.json({ clickCount: product.clickCount });
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
