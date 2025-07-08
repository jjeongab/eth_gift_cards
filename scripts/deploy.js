const hre = require("hardhat");

async function main() {
  console.log("Deploying GiftCard contract...");

  const GiftCard = await hre.ethers.getContractFactory("GiftCard");
  const giftCard = await GiftCard.deploy();

  await giftCard.deployed();

  console.log("GiftCard contract deployed to:", giftCard.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });