const hre = require("hardhat");

async function main() {
  console.log("Deploying GiftCard contract...");

  const GiftCard = await hre.ethers.getContractFactory("GiftCard");
  const giftCard = await GiftCard.deploy();

  // New syntax - wait for deployment
  await giftCard.waitForDeployment();

  // New syntax - get address
  const address = await giftCard.getAddress();

  console.log("GiftCard contract deployed to:", address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });