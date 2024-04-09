from scripts.prefect_scripts.my_gh_sample_transfer_workflow import move_sample

sample_link = "https://pioreactor.com/en-ca/collections/accessories-and-parts/products/20ml-glass-vial-closed-cap-and-stir-bar?variant=42836211761208"  # noqa: E501
sample_name = "sample_100d793c"
source_link = "https://ca.robotshop.com/products/dh-robotics-automated-screw-cap-decapper-intelligent-capping-machine"  # noqa: E501
source_name = "Automated capper/decapper"
destination_link = "https://autotrickler.com/pages/autotrickler-v4"
destination_name = "Autotrickler v4"

move_sample(
    sample_link,
    sample_name,
    source_link,
    source_name,
    destination_link,
    destination_name,
)
