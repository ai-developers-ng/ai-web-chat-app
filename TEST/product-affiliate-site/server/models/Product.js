const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, required: true },
  images: [String],
  rating: { type: Number, min: 0, max: 5, default: 0 },
  affiliateLink: { type: String },
  category: { type: mongoose.Schema.Types.ObjectId, ref: 'Category' },
  clickCount: { type: Number, default: 0 },
}, { timestamps: true });

module.exports = mongoose.model('Product', productSchema);
