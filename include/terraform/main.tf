

module "storage" {
  source        = "./modules/storage"
  buckets_names = ["anass-bucket-dataops", "ayoub-bucket-dataops"]

}
